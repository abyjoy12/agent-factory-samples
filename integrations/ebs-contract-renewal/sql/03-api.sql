-- Run as APPS. Runtime receives EXECUTE on XXAF_RENEWAL_API only.
whenever sqlerror exit failure rollback
set define off
create or replace package XXAF_RENEWAL_API authid definer as
  function get_bpa_snapshot(p_source_header_id number) return clob;
  function stage_renewal(p_source_header_id number, p_start_date varchar2,
    p_end_date varchar2, p_uplift_pct number, p_evidence_ref varchar2,
    p_idempotency_key varchar2) return clob;
  function validate_renewal(p_draft_id number) return clob;
  function submit_reviewed_renewal(p_draft_id number) return clob;
  function get_renewal_status(p_draft_id number) return clob;
end XXAF_RENEWAL_API;
/
create or replace package body XXAF_RENEWAL_API as
  function scope_row return XXAF_RNW_SCOPE%rowtype is
    s XXAF_RNW_SCOPE%rowtype; n number;
  begin
    select * into s from XXAF_RNW_SCOPE where db_username=sys_context('USERENV','SESSION_USER') and enabled_flag='Y';
    select count(*) into n from fnd_user u
      join fnd_user_resp_groups_direct ur on ur.user_id=u.user_id
      join fnd_responsibility r on r.responsibility_id=ur.responsibility_id
        and r.application_id=ur.responsibility_application_id
      where u.user_id=s.user_id and r.responsibility_id=s.responsibility_id
        and r.application_id=s.application_id
        and sysdate between nvl(u.start_date,sysdate-1) and nvl(u.end_date,sysdate+1)
        and sysdate between nvl(ur.start_date,sysdate-1) and nvl(ur.end_date,sysdate+1)
        and sysdate between nvl(r.start_date,sysdate-1) and nvl(r.end_date,sysdate+1);
    if n=0 then raise_application_error(-20001,'EBS user/responsibility is inactive'); end if;
    return s;
  exception when no_data_found then
    raise_application_error(-20001,'This database identity has no renewal scope');
  end;

  procedure enter_context(s XXAF_RNW_SCOPE%rowtype) is
  begin
    fnd_global.apps_initialize(s.user_id,s.responsibility_id,s.application_id);
    mo_global.init('PO');
    if not mo_global.check_access(s.org_id)='Y' then
      raise_application_error(-20001,'Operating unit is outside EBS responsibility');
    end if;
    mo_global.set_policy_context('S',s.org_id);
  end;

  procedure clear_context is
  begin
    mo_global.set_policy_context('S',null);
    fnd_global.apps_initialize(-1,-1,-1);
  end;

  procedure audit_event(p_id number,p_user number,p_event varchar2,p_detail varchar2) is
  begin
    insert into XXAF_RNW_AUDIT(audit_id,draft_id,db_username,user_id,event_name,event_detail)
    values(XXAF_RNW_S.nextval,p_id,sys_context('USERENV','SESSION_USER'),p_user,p_event,substr(p_detail,1,1000));
  end;

  function digest(p_json clob) return varchar2 is
  begin return lower(rawtohex(dbms_crypto.hash(p_json,dbms_crypto.hash_sh256))); end;

  function snapshot(p_id number,s XXAF_RNW_SCOPE%rowtype) return clob is
    result clob; n number;
  begin
    if p_id is null or p_id<>s.source_header_id then
      raise_application_error(-20002,'Source BPA is outside this identity scope');
    end if;
    select count(*) into n from po_lines_all where po_header_id=p_id;
    if n<1 or n>100 then raise_application_error(-20003,'Source must have 1 to 100 lines'); end if;
    select json_object(
      'header_id' value h.po_header_id, 'number' value h.segment1,
      'org_id' value h.org_id, 'type' value h.type_lookup_code,
      'revision' value nvl(h.revision_num,0),'status' value h.authorization_status,
      'cancelled' value nvl(h.cancel_flag,'N'), 'closed' value h.closed_code,
      'global' value nvl(h.global_agreement_flag,'N'),
      'buyer_id' value h.agent_id,'supplier_id' value h.vendor_id,
      'supplier_site_id' value h.vendor_site_id,'currency' value h.currency_code,
      'ship_to' value h.ship_to_location_id,'bill_to' value h.bill_to_location_id,
      'terms_id' value h.terms_id,'fob' value h.fob_lookup_code,
      'freight_terms' value h.freight_terms_lookup_code,'style_id' value h.style_id,
      'start_date' value to_char(h.start_date,'YYYY-MM-DD'),
      'end_date' value to_char(h.end_date,'YYYY-MM-DD'),
      'lines' value (select json_arrayagg(json_object(
        'source_line_id' value l.po_line_id,'line_num' value l.line_num,
        'line_type_id' value l.line_type_id,'item_id' value l.item_id,
        'category_id' value l.category_id,'description' value l.item_description,
        'uom' value l.unit_meas_lookup_code,'price' value l.unit_price,
        'cancelled' value nvl(l.cancel_flag,'N'),'closed' value l.closed_code,
        'expiration_date' value to_char(l.expiration_date,'YYYY-MM-DD'))
        order by l.line_num returning clob) from po_lines_all l
        where l.po_header_id=h.po_header_id) format json returning clob)
    into result from po_headers_all h where h.po_header_id=p_id and h.org_id=s.org_id;
    return result;
  exception when no_data_found then raise_application_error(-20002,'Source BPA not accessible');
  end;

  function select_employee(p_user number) return number is n number;
  begin select employee_id into n from fnd_user where user_id=p_user; return n; end;

  function select_line_count(p_id number) return number is n number;
  begin select count(*) into n from XXAF_RNW_LINES where draft_id=p_id; return n; end;

  procedure assert_source(p_id number,s XXAF_RNW_SCOPE%rowtype) is
    h po_headers_all%rowtype; n number;
  begin
    if p_id is null or p_id<>s.source_header_id then
      raise_application_error(-20002,'Source BPA is outside this identity scope');
    end if;
    select * into h from po_headers_all where po_header_id=p_id and org_id=s.org_id;
    if h.type_lookup_code<>'BLANKET' or nvl(h.authorization_status,'?')<>'APPROVED'
       or nvl(h.cancel_flag,'N')<>'N' or nvl(h.closed_code,'OPEN')<>'OPEN'
       or nvl(h.global_agreement_flag,'N')<>'N' then
      raise_application_error(-20003,'Source must be an open approved local BPA');
    end if;
    -- Phase one deliberately supports the verified USD goods configuration only.
    if nvl(h.currency_code,'?')<>'USD' or nvl(h.agent_id,-1)<>nvl(select_employee(s.user_id),-2) then
      raise_application_error(-20003,'Source currency or buyer is outside supported scope');
    end if;
    select count(*) into n from ap_suppliers v join ap_supplier_sites_all vs
      on vs.vendor_id=v.vendor_id join po_agents a on a.agent_id=h.agent_id
      where v.vendor_id=h.vendor_id and vs.vendor_site_id=h.vendor_site_id
        and vs.org_id=s.org_id and v.enabled_flag='Y' and vs.purchasing_site_flag='Y'
        and nvl(v.start_date_active,sysdate-1)<=sysdate
        and nvl(v.end_date_active,sysdate+1)>sysdate
        and nvl(vs.inactive_date,sysdate+1)>sysdate
        and nvl(a.start_date_active,sysdate-1)<=sysdate
        and nvl(a.end_date_active,sysdate+1)>sysdate;
    if n<>1 then raise_application_error(-20003,'Supplier, purchasing site or buyer inactive'); end if;
    if h.ship_to_location_id is null or h.bill_to_location_id is null or h.terms_id is null then
      raise_application_error(-20003,'Source is missing locations or payment terms');
    end if;
    select count(*) into n from po_lines_all l
      where l.po_header_id=p_id and (nvl(l.cancel_flag,'N')<>'N'
        or nvl(l.closed_code,'OPEN')<>'OPEN' or l.item_id is null
        or l.line_type_id<>1 or l.category_id is null
        or l.unit_meas_lookup_code is null or nvl(l.unit_price,0)<=0
        or not exists(select 1 from mtl_system_items_b i
          join financials_system_params_all f on f.inventory_organization_id=i.organization_id
          where f.org_id=s.org_id and i.inventory_item_id=l.item_id
            and i.purchasing_enabled_flag='Y' and i.purchasing_item_flag='Y'
            and nvl(i.start_date_active,sysdate-1)<=sysdate
            and nvl(i.end_date_active,sysdate+1)>sysdate)
        or not exists(select 1 from mtl_units_of_measure u
          where u.unit_of_measure=l.unit_meas_lookup_code
            and nvl(u.disable_date,sysdate+1)>sysdate));
    if n<>0 then raise_application_error(-20003,'Source has unsupported/inactive goods lines'); end if;
  exception when no_data_found then raise_application_error(-20002,'Source BPA not accessible');
  end;

  function status_json(p_id number) return clob is result clob;
  begin
    select json_object('draft_id' value d.draft_id,'status' value d.status,
      'source_header_id' value d.source_header_id,'source_revision' value d.source_revision,
      'draft_hash' value d.draft_hash,'source_hash' value d.source_hash,
      'start_date' value to_char(d.start_date,'YYYY-MM-DD'),
      'end_date' value to_char(d.end_date,'YYYY-MM-DD'),'uplift_pct' value d.uplift_pct,
      'evidence_ref' value d.evidence_ref,'batch_id' value d.batch_id,
      'request_id' value d.request_id,'bpa_header_id' value d.result_header_id,
      'bpa_number' value d.result_number,'ebs_status' value d.result_status,
      'request' value (select json_object('phase' value r.phase_code,'status' value r.status_code,
        'message' value substr(r.completion_text,1,500)) from fnd_concurrent_requests r
        where r.request_id=d.request_id) format json,
      'lines' value (select json_arrayagg(json_object('line_num' value l.line_num,
        'item_id' value l.item_id,'description' value l.item_description,
        'uom' value l.unit_of_measure,'old_price' value l.old_price,'new_price' value l.new_price)
        order by l.line_num returning clob) from XXAF_RNW_LINES l where l.draft_id=d.draft_id) format json,
      'errors' value (select json_arrayagg(json_object('column' value e.column_name,
        'message' value substr(e.error_message,1,500)) returning clob)
        from (select column_name,error_message from po_interface_errors
          where interface_header_id=d.interface_header_id and rownum<=10) e) format json
      returning clob) into result from XXAF_RNW_DRAFTS d where draft_id=p_id;
    return result;
  end;

  procedure lock_draft(p_id number,s XXAF_RNW_SCOPE%rowtype,d out XXAF_RNW_DRAFTS%rowtype) is
  begin
    select * into d from XXAF_RNW_DRAFTS where draft_id=p_id
      and db_username=sys_context('USERENV','SESSION_USER') and org_id=s.org_id and source_header_id=s.source_header_id
      for update wait 5;
  exception when no_data_found then raise_application_error(-20002,'Draft not accessible');
  end;

  procedure validate_draft(d XXAF_RNW_DRAFTS%rowtype,s XXAF_RNW_SCOPE%rowtype) is n number;
  begin
    assert_source(d.source_header_id,s);
    if d.start_date<trunc(sysdate) or d.end_date<d.start_date or d.end_date>=d.start_date+366 then
      raise_application_error(-20004,'Renewal must start today or later and last at most 366 days');
    end if;
    if digest(snapshot(d.source_header_id,s))<>d.source_hash then
      raise_application_error(-20005,'Source BPA changed; stage a new renewal');
    end if;
    select count(*) into n from XXAF_RNW_LINES where draft_id=d.draft_id
      and (new_price<>round(old_price*(1+d.uplift_pct/100),2) or new_price<=0);
    if n<>0 then raise_application_error(-20005,'Draft price integrity check failed'); end if;
  end;

  function get_bpa_snapshot(p_source_header_id number) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; result clob;
  begin
    s:=scope_row; enter_context(s); result:=snapshot(p_source_header_id,s);
    clear_context; rollback; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;

  function stage_renewal(p_source_header_id number,p_start_date varchar2,
    p_end_date varchar2,p_uplift_pct number,p_evidence_ref varchar2,
    p_idempotency_key varchar2) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype;
    v_start date; v_end date; v_snapshot clob; v_hash varchar2(64);
    v_draft_hash varchar2(64); result clob;
  begin
    s:=scope_row; enter_context(s);
    if p_idempotency_key is null or length(p_idempotency_key)>100
      or not regexp_like(p_idempotency_key,'^[A-Za-z0-9_.:-]+$') then
      raise_application_error(-20004,'A 1 to 100 character idempotency key is required'); end if;
    if p_evidence_ref is null or length(p_evidence_ref)>1000 then
      raise_application_error(-20004,'A bounded evidence/review reference is required'); end if;
    if p_uplift_pct is null or p_uplift_pct<0 or p_uplift_pct>10 then
      raise_application_error(-20004,'Price uplift must be between 0 and 10 percent'); end if;
    v_start:=to_date(p_start_date,'FXYYYY-MM-DD'); v_end:=to_date(p_end_date,'FXYYYY-MM-DD');
    -- A retry returns the original outcome even after the source or date has changed.
    begin
      select * into d from XXAF_RNW_DRAFTS where db_username=sys_context('USERENV','SESSION_USER') and idempotency_key=p_idempotency_key;
      if d.source_header_id<>p_source_header_id or d.start_date<>v_start or d.end_date<>v_end
        or d.uplift_pct<>p_uplift_pct or d.evidence_ref<>p_evidence_ref then
        raise_application_error(-20006,'Idempotency key already belongs to another payload'); end if;
      result:=status_json(d.draft_id); clear_context; rollback; return result;
    exception when no_data_found then null; end;
    if v_start is null or v_end is null or v_start<trunc(sysdate)
      or v_end<v_start or v_end>=v_start+366 then
      raise_application_error(-20004,'Dates must define a future term of at most 366 days'); end if;
    assert_source(p_source_header_id,s);
    v_snapshot:=snapshot(p_source_header_id,s); v_hash:=digest(v_snapshot);
    v_draft_hash:=digest(v_snapshot||'|'||to_char(v_start,'YYYYMMDD')||'|'||
      to_char(v_end,'YYYYMMDD')||'|'||to_char(p_uplift_pct,'FM990D999999','NLS_NUMERIC_CHARACTERS=''.,''')||'|'||p_evidence_ref);
    d.draft_id:=XXAF_RNW_S.nextval;
    select nvl(revision_num,0) into d.source_revision from po_headers_all where po_header_id=p_source_header_id;
    insert into XXAF_RNW_LINES(draft_id,source_line_id,line_num,line_type_id,item_id,
      category_id,item_description,unit_of_measure,old_price,new_price)
      select d.draft_id,po_line_id,line_num,line_type_id,item_id,category_id,
        item_description,unit_meas_lookup_code,unit_price,round(unit_price*(1+p_uplift_pct/100),2)
      from po_lines_all where po_header_id=p_source_header_id;
    insert into XXAF_RNW_DRAFTS(draft_id,db_username,idempotency_key,source_header_id,
      source_revision,org_id,source_snapshot,source_hash,draft_hash,start_date,end_date,
      uplift_pct,evidence_ref,created_by)
      values(d.draft_id,sys_context('USERENV','SESSION_USER'),p_idempotency_key,p_source_header_id,d.source_revision,
        s.org_id,v_snapshot,v_hash,v_draft_hash,
        v_start,v_end,p_uplift_pct,p_evidence_ref,s.user_id);
    audit_event(d.draft_id,s.user_id,'STAGED','Immutable renewal draft created');
    result:=status_json(d.draft_id); clear_context; commit; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;

  function validate_renewal(p_draft_id number) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype; result clob;
  begin
    s:=scope_row; enter_context(s); lock_draft(p_draft_id,s,d);
    if d.status not in ('STAGED','VALIDATED') then
      raise_application_error(-20007,'Only an unreviewed draft can be validated'); end if;
    validate_draft(d,s);
    update XXAF_RNW_DRAFTS set status='VALIDATED',updated_at=systimestamp where draft_id=p_draft_id;
    audit_event(p_draft_id,s.user_id,'VALIDATED','Source and deterministic price/date rules checked');
    result:=status_json(p_draft_id); clear_context; commit; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;

  function submit_reviewed_renewal(p_draft_id number) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype; r XXAF_RNW_REVIEWS%rowtype;
    h po_headers_all%rowtype; result clob; v_request number; v_header number;
  begin
    s:=scope_row; enter_context(s); lock_draft(p_draft_id,s,d);
    if d.request_id is not null then
      result:=status_json(p_draft_id); clear_context; rollback; return result;
    end if;
    if d.status<>'REVIEWED' then raise_application_error(-20008,'Trusted review is required'); end if;
    select * into r from XXAF_RNW_REVIEWS where draft_id=p_draft_id for update;
    if r.draft_hash<>d.draft_hash or r.expires_at<=systimestamp or r.consumed_at is not null then
      raise_application_error(-20008,'Review is expired, consumed or does not match this draft'); end if;
    -- Serialize with source header changes during validation/interface submission.
    select * into h from po_headers_all where po_header_id=d.source_header_id for update wait 5;
    validate_draft(d,s);
    select po_headers_interface_s.nextval into v_header from dual;
    insert into po_headers_interface(interface_header_id,batch_id,interface_source_code,
      process_code,action,org_id,document_type_code,currency_code,agent_id,vendor_id,
      vendor_site_id,ship_to_location_id,bill_to_location_id,terms_id,fob,freight_terms,
      approval_status,effective_date,expiration_date,comments,reference_num,
      load_sourcing_rules_flag,global_agreement_flag,style_id,
      created_by,creation_date,last_updated_by,last_update_date)
    values(v_header,v_header,'XXAF_RENEWAL','PENDING','ORIGINAL',s.org_id,'BLANKET',
      h.currency_code,h.agent_id,h.vendor_id,h.vendor_site_id,h.ship_to_location_id,
      h.bill_to_location_id,h.terms_id,h.fob_lookup_code,h.freight_terms_lookup_code,
      'INCOMPLETE',d.start_date,d.end_date,
      substr('Renewal of BPA '||h.segment1||'; draft '||to_char(p_draft_id),1,240),
      substr(h.segment1,1,25),'N','N',h.style_id,s.user_id,sysdate,s.user_id,sysdate);
    insert into po_lines_interface(interface_line_id,interface_header_id,action,
      process_code,line_num,line_type_id,item_id,category_id,item_description,
      unit_of_measure,unit_price,expiration_date,
      created_by,creation_date,last_updated_by,last_update_date)
    select po_lines_interface_s.nextval,v_header,'ADD','PENDING',line_num,line_type_id,
      item_id,category_id,item_description,unit_of_measure,new_price,d.end_date,
      s.user_id,sysdate,s.user_id,sysdate from XXAF_RNW_LINES where draft_id=p_draft_id;
    -- Installed R12.2.14 POXPDOI parameter order: batch is argument 8, OU is 9.
    v_request:=fnd_request.submit_request(application=>'PO',program=>'POXPDOI',
      description=>'Reviewed BPA renewal draft '||to_char(p_draft_id),
      start_time=>null,sub_request=>false,
      argument1=>to_char(h.agent_id),argument2=>'BLANKET',argument3=>null,
      argument4=>'N',argument5=>'N',argument6=>'INCOMPLETE',argument7=>null,
      argument8=>to_char(v_header),argument9=>to_char(s.org_id),argument10=>'N',
      argument11=>'N',argument12=>null,argument13=>'N',argument14=>null,
      argument15=>'N',argument16=>'N',argument17=>'100',argument18=>'N');
    if v_request=0 then raise_application_error(-20009,'Import request rejected: '||fnd_message.get); end if;
    update XXAF_RNW_DRAFTS set status='SUBMITTED',interface_header_id=v_header,
      batch_id=v_header,request_id=v_request,updated_at=systimestamp where draft_id=p_draft_id;
    update XXAF_RNW_REVIEWS set consumed_at=systimestamp where draft_id=p_draft_id;
    audit_event(p_draft_id,s.user_id,'SUBMITTED','Import Price Catalogs request '||to_char(v_request));
    result:=status_json(p_draft_id); clear_context; commit; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;

  function get_renewal_status(p_draft_id number) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype;
    v_phase varchar2(1); v_process varchar2(25); v_header number;
    v_number varchar2(25); v_status varchar2(25); n number; v_total number; result clob;
  begin
    s:=scope_row; enter_context(s); lock_draft(p_draft_id,s,d);
    if d.status='SUBMITTED' then
      select phase_code into v_phase from fnd_concurrent_requests where request_id=d.request_id;
      if v_phase='C' then
        begin
          select process_code,po_header_id into v_process,v_header from po_headers_interface
            where interface_header_id=d.interface_header_id and batch_id=d.batch_id;
        exception when no_data_found then
          -- Recover after an operator purges accepted interface rows. Each submitted
          -- request has exactly one header, with this source marker and creator.
          select po_header_id,'ACCEPTED' into v_header,v_process from po_headers_all
            where request_id=d.request_id and interface_source_code='XXAF_RENEWAL'
              and org_id=d.org_id and created_by=d.created_by and type_lookup_code='BLANKET';
        end;
        if v_process='ACCEPTED' and v_header is not null and v_header<>d.source_header_id then
          select segment1,authorization_status into v_number,v_status from po_headers_all
            where po_header_id=v_header and org_id=d.org_id and type_lookup_code='BLANKET'
              and trunc(start_date)=d.start_date and trunc(end_date)=d.end_date
              and request_id=d.request_id and interface_source_code='XXAF_RENEWAL';
          select count(*) into n from po_lines_all l join XXAF_RNW_LINES x
            on x.draft_id=p_draft_id and x.line_num=l.line_num
            where l.po_header_id=v_header and l.item_id=x.item_id and l.unit_price=x.new_price
              and l.line_type_id=x.line_type_id and l.category_id=x.category_id
              and l.unit_meas_lookup_code=x.unit_of_measure and trunc(l.expiration_date)=d.end_date;
          select count(*) into v_total from po_lines_all where po_header_id=v_header;
          if nvl(v_status,'?')<>'INCOMPLETE' or n<>select_line_count(p_draft_id) or n<>v_total then
            raise_application_error(-20010,'Imported result requires operator investigation'); end if;
          update XXAF_RNW_DRAFTS set status='IMPORTED',result_header_id=v_header,
            result_number=v_number,result_status=v_status,updated_at=systimestamp where draft_id=p_draft_id;
          audit_event(p_draft_id,s.user_id,'IMPORTED','New BPA '||v_number||' is INCOMPLETE');
        else
          update XXAF_RNW_DRAFTS set status='IMPORT_FAILED',updated_at=systimestamp where draft_id=p_draft_id;
          audit_event(p_draft_id,s.user_id,'IMPORT_FAILED','Inspect bounded interface errors and concurrent log');
        end if;
      end if;
    end if;
    if d.status='IMPORTED' then
      -- EBS buyers can subsequently edit or approve the document in the application.
      -- Preserve the creation receipt but report its current authorization status.
      select authorization_status into v_status from po_headers_all
        where po_header_id=d.result_header_id and org_id=d.org_id and type_lookup_code='BLANKET';
      if nvl(v_status,'?')<>nvl(d.result_status,'?') then
        update XXAF_RNW_DRAFTS set result_status=v_status,updated_at=systimestamp where draft_id=p_draft_id;
        audit_event(p_draft_id,s.user_id,'STATUS_REFRESHED','Current EBS status: '||v_status);
      end if;
    end if;
    result:=status_json(p_draft_id); clear_context; commit; return result;
  exception
    when no_data_found then
      rollback; clear_context; rollback;
      raise_application_error(-20010,'Expected import records absent; operator investigation required');
    when too_many_rows then
      rollback; clear_context; rollback;
      raise_application_error(-20010,'Import result is ambiguous; operator investigation required');
    when others then rollback; clear_context; rollback; raise;
  end;
end XXAF_RENEWAL_API;
/
show errors

-- This package is intentionally NOT granted to the runtime database identity.
create or replace package XXAF_RENEWAL_ADMIN authid definer as
  procedure approve_draft(p_draft_id number,p_expected_hash varchar2,p_reason varchar2);
end XXAF_RENEWAL_ADMIN;
/
create or replace package body XXAF_RENEWAL_ADMIN as
  procedure approve_draft(p_draft_id number,p_expected_hash varchar2,p_reason varchar2) is
    d XXAF_RNW_DRAFTS%rowtype;
  begin
    if sys_context('USERENV','SESSION_USER')<>'APPS' then
      raise_application_error(-20001,'Trusted review operator required'); end if;
    if p_reason is null or length(p_reason)>1000 or p_expected_hash is null then
      raise_application_error(-20004,'Exact draft hash and review reason required'); end if;
    select * into d from XXAF_RNW_DRAFTS where draft_id=p_draft_id for update wait 5;
    if d.status<>'VALIDATED' or d.draft_hash<>p_expected_hash then
      raise_application_error(-20008,'Review requires the exact validated draft'); end if;
    insert into XXAF_RNW_REVIEWS(draft_id,draft_hash,reviewer,review_reason,expires_at)
      values(p_draft_id,p_expected_hash,sys_context('USERENV','SESSION_USER'),p_reason,systimestamp+interval '1' hour);
    update XXAF_RNW_DRAFTS set status='REVIEWED',updated_at=systimestamp where draft_id=p_draft_id;
    insert into XXAF_RNW_AUDIT(audit_id,draft_id,db_username,user_id,event_name,event_detail)
      values(XXAF_RNW_S.nextval,p_draft_id,sys_context('USERENV','SESSION_USER'),null,'REVIEWED',p_reason);
    -- The operator commits only after inspecting the review result.
  end;
end XXAF_RENEWAL_ADMIN;
/
show errors
begin
  for e in (select name,type,line,text from user_errors where name in
    ('XXAF_RENEWAL_API','XXAF_RENEWAL_ADMIN') order by name,sequence) loop
    raise_application_error(-20099,e.name||' '||e.line||' '||e.text);
  end loop;
end;
/
