-- Demo email/chat review using the existing scoped runtime login. No PAF patch.
-- Run DBA, APPS, then DBA phases in the EBS PDB run edition after scripts 01-05.
-- The known code 6004 is a demo confirmation, NOT authenticated identity proof.
whenever sqlerror exit failure rollback
set define off
create table XXAF_RENEWAL.XXAF_RNW_EMAIL_REQUESTS (
  draft_id number primary key, db_username varchar2(128) not null,
  draft_hash varchar2(64) not null, recipient varchar2(254) not null,
  requested_at timestamp default systimestamp not null,
  expires_at timestamp not null, attempts number default 0 not null,
  state varchar2(12) default 'PENDING' not null,
  constraint XXAF_RNW_EMAIL_STATE check(state in ('PENDING','APPROVED','BLOCKED'))
);
grant select,insert,update on XXAF_RENEWAL.XXAF_RNW_EMAIL_REQUESTS to APPS;
-- BEGIN APPS PHASE (connect as APPS; never grant inheritance of SYS privileges)
begin
  APPS.AD_ZD_TABLE.UPGRADE('XXAF_RENEWAL','XXAF_RNW_EMAIL_REQUESTS');
end;
/
alter session set current_schema=APPS;
create or replace package XXAF_RENEWAL_EMAIL authid definer as
  function request_review(p_draft_id number,p_expected_hash varchar2,
    p_recipient varchar2) return clob;
  function confirm_review(p_draft_id number,p_expected_hash varchar2,
    p_recipient varchar2,p_code varchar2,p_reason varchar2) return clob;
end XXAF_RENEWAL_EMAIL;
/
create or replace package body XXAF_RENEWAL_EMAIL as
  function scope_row return XXAF_RNW_SCOPE%rowtype is
    s XXAF_RNW_SCOPE%rowtype; n number;
  begin
    select * into s from XXAF_RNW_SCOPE
      where db_username=sys_context('USERENV','SESSION_USER') and enabled_flag='Y';
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
    fnd_global.apps_initialize(s.user_id,s.responsibility_id,s.application_id);
    mo_global.init('PO');
    if not mo_global.check_access(s.org_id)='Y' then
      raise_application_error(-20001,'Operating unit is outside EBS responsibility'); end if;
    mo_global.set_policy_context('S',s.org_id);
    return s;
  exception when no_data_found then
    raise_application_error(-20001,'This database identity has no renewal scope');
  end;

  procedure clear_context is
  begin
    mo_global.set_policy_context('S',null);
    fnd_global.apps_initialize(-1,-1,-1);
  end;

  function recipient(p_value varchar2) return varchar2 is v varchar2(254);
  begin
    if p_value is null or length(p_value)>254
      or not regexp_like(p_value,'^[A-Za-z0-9.!#$%&''*+/=?^_`{|}~-]+@[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}$') then
      raise_application_error(-20004,'One explicit recipient email address is required'); end if;
    v:=lower(p_value); return v;
  end;

  procedure lock_draft(p_id number,p_hash varchar2,s XXAF_RNW_SCOPE%rowtype,
    d out XXAF_RNW_DRAFTS%rowtype) is
  begin
    if p_hash is null or length(p_hash)<>64 then
      raise_application_error(-20008,'Exact immutable draft hash required'); end if;
    select * into d from XXAF_RNW_DRAFTS where draft_id=p_id
      and db_username=sys_context('USERENV','SESSION_USER')
      and org_id=s.org_id and source_header_id=s.source_header_id for update wait 5;
    if d.draft_hash<>p_hash then
      raise_application_error(-20008,'Draft hash does not match'); end if;
  exception when no_data_found then raise_application_error(-20002,'Draft not accessible');
  end;

  procedure audit_event(p_id number,p_user number,p_event varchar2,p_detail varchar2) is
  begin
    insert into XXAF_RNW_AUDIT(audit_id,draft_id,db_username,user_id,event_name,event_detail)
      values(XXAF_RNW_S.nextval,p_id,sys_context('USERENV','SESSION_USER'),
        p_user,p_event,substr(p_detail,1,1000));
  end;

  function escaped(p_text varchar2) return varchar2 is
  begin
    return replace(replace(replace(replace(p_text,'&','&amp;'),'<','&lt;'),'>','&gt;'),chr(10),'<br>');
  end;

  function email_text(p_text varchar2) return varchar2 is
  begin
    -- The existing email tool uses HTML MIME even for text. Escape data without
    -- adding markup, so its literal chat preview stays readable and inert.
    return replace(replace(replace(replace(replace(p_text,'&','&amp;'),
      '<','&lt;'),'>','&gt;'),chr(13),' '),chr(10),' ');
  end;

  function request_json(d XXAF_RNW_DRAFTS%rowtype,r XXAF_RNW_EMAIL_REQUESTS%rowtype) return clob is
    body_html clob; body_text clob; result clob; src json_object_t; prices varchar2(240);
  begin
    src:=json_object_t.parse(d.source_snapshot);
    body_html:='<h2>Review BPA renewal draft '||to_char(d.draft_id)||'</h2><p>Source BPA: '||
      escaped(src.get_string('number'))||'; revision '||to_char(d.source_revision)||
      '; operating unit '||to_char(d.org_id)||'; supplier '||src.get_number('supplier_id')||
      '; supplier site '||src.get_number('supplier_site_id')||'; currency '||escaped(src.get_string('currency'))||
      '</p><p>Dates: '||to_char(d.start_date,'YYYY-MM-DD')||' through '||to_char(d.end_date,'YYYY-MM-DD')||
      '; uniform price uplift: '||to_char(d.uplift_pct)||'%.</p><ul>';
    body_text:='Review BPA renewal draft '||to_char(d.draft_id)||'.'||chr(10)||chr(10)||
      'Source BPA: '||email_text(src.get_string('number'))||'; revision '||to_char(d.source_revision)||
      '; operating unit '||to_char(d.org_id)||'; supplier '||src.get_number('supplier_id')||
      '; supplier site '||src.get_number('supplier_site_id')||'; currency '||email_text(src.get_string('currency'))||'.'||chr(10)||
      'Dates: '||to_char(d.start_date,'YYYY-MM-DD')||' through '||to_char(d.end_date,'YYYY-MM-DD')||
      '; uniform price uplift: '||to_char(d.uplift_pct)||'%.'||chr(10)||chr(10);
    for l in (select * from XXAF_RNW_LINES where draft_id=d.draft_id order by line_num) loop
      prices:=to_char(l.old_price,'FM999999999999990D00','NLS_NUMERIC_CHARACTERS=''.,''')||
        ' to '||to_char(l.new_price,'FM999999999999990D00','NLS_NUMERIC_CHARACTERS=''.,''');
      body_html:=body_html||'<li>Line '||l.line_num||': '||escaped(l.item_description)||
        '; item '||l.item_id||'; '||escaped(l.unit_of_measure)||'; USD '||prices||'</li>';
      body_text:=body_text||'Line '||l.line_num||': '||email_text(l.item_description)||
        '; item '||l.item_id||'; '||email_text(l.unit_of_measure)||'; USD '||prices||'.'||chr(10);
    end loop;
    body_html:=body_html||'</ul><p>Evidence and gaps: '||escaped(d.evidence_ref)||
      '</p><p>Exact draft hash: <code>'||d.draft_hash||'</code></p>'||
      '<p>Demo approval code: <strong>6004</strong>. Request expires at '||
      to_char(r.expires_at,'YYYY-MM-DD HH24:MI:SS')||' database local time.</p>'||
      '<p>After inspecting all terms, return to the renewal chat and enter: '||
      'Approve draft '||d.draft_id||' with code 6004. Reason: [your review reason].</p>'||
      '<p>This fixed code is for demonstration, not proof of identity. Approval records the exact draft; '||
      'it does not import it or approve the resulting EBS agreement. An import requires a separate request '||
      'and creates an Incomplete BPA for buyer inspection. To decline, do not enter approval; request changed terms as a new draft.</p>';
    body_text:=body_text||chr(10)||'Evidence and gaps: '||email_text(d.evidence_ref)||'.'||chr(10)||chr(10)||
      'Exact draft hash: '||d.draft_hash||'.'||chr(10)||chr(10)||
      'Demo approval code: 6004. Request expires at '||
      to_char(r.expires_at,'YYYY-MM-DD HH24:MI:SS')||' database local time.'||chr(10)||chr(10)||
      'After inspecting all terms, return to the renewal chat and enter: Approve draft '||d.draft_id||
      ' with code 6004. Reason: [your review reason].'||chr(10)||chr(10)||
      'This fixed code is for demonstration, not proof of identity. Approval records the exact draft; '||
      'it does not import it or approve the resulting EBS agreement. An import requires a separate request '||
      'and creates an Incomplete BPA for buyer inspection. To decline, do not enter approval; request changed terms as a new draft.';
    select json_object('draft_id' value d.draft_id,'draft_hash' value d.draft_hash,
      'state' value r.state,'recipient' value r.recipient,
      'expires_at' value to_char(r.expires_at,'YYYY-MM-DD HH24:MI:SS'),
      'email_subject' value 'Review BPA renewal draft '||to_char(d.draft_id),
      'email_body_text' value body_text,'email_body_html' value body_html,
      'email_delivery_verified' value 'false' format json,
      'demo_code' value '6004' returning clob) into result from dual;
    return result;
  end;

  function request_review(p_draft_id number,p_expected_hash varchar2,
    p_recipient varchar2) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype;
    r XXAF_RNW_EMAIL_REQUESTS%rowtype; v_email varchar2(254); result clob;
  begin
    s:=scope_row; v_email:=recipient(p_recipient); lock_draft(p_draft_id,p_expected_hash,s,d);
    if d.status<>'VALIDATED' then
      raise_application_error(-20008,'Email review requires a validated unreviewed draft'); end if;
    begin
      select * into r from XXAF_RNW_EMAIL_REQUESTS where draft_id=p_draft_id for update;
      if r.db_username<>d.db_username or r.draft_hash<>d.draft_hash or r.recipient<>v_email then
        raise_application_error(-20008,'Existing review request has different scope or recipient'); end if;
      if r.expires_at>systimestamp then
        if r.state<>'PENDING' then raise_application_error(-20008,'Review request is blocked'); end if;
        result:=request_json(d,r); clear_context; rollback; return result;
      end if;
      update XXAF_RNW_EMAIL_REQUESTS set requested_at=systimestamp,
        expires_at=systimestamp+interval '30' minute,attempts=0,state='PENDING' where draft_id=p_draft_id;
    exception when no_data_found then
      insert into XXAF_RNW_EMAIL_REQUESTS(draft_id,db_username,draft_hash,recipient,expires_at)
        values(d.draft_id,d.db_username,d.draft_hash,v_email,systimestamp+interval '30' minute);
    end;
    select * into r from XXAF_RNW_EMAIL_REQUESTS where draft_id=p_draft_id;
    audit_event(p_draft_id,s.user_id,'EMAIL_REVIEW_REQUESTED','Recipient: '||v_email||'; fixed-code demo');
    result:=request_json(d,r); clear_context; commit; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;

  function confirm_review(p_draft_id number,p_expected_hash varchar2,
    p_recipient varchar2,p_code varchar2,p_reason varchar2) return clob is
    pragma autonomous_transaction;
    s XXAF_RNW_SCOPE%rowtype; d XXAF_RNW_DRAFTS%rowtype;
    r XXAF_RNW_EMAIL_REQUESTS%rowtype; v XXAF_RNW_REVIEWS%rowtype;
    v_email varchar2(254); result clob;
  begin
    s:=scope_row; v_email:=recipient(p_recipient); lock_draft(p_draft_id,p_expected_hash,s,d);
    begin
      select * into r from XXAF_RNW_EMAIL_REQUESTS where draft_id=p_draft_id for update;
    exception when no_data_found then raise_application_error(-20008,'Request email review first'); end;
    if r.db_username<>d.db_username or r.draft_hash<>d.draft_hash or r.recipient<>v_email then
      raise_application_error(-20008,'Review request scope does not match'); end if;
    if p_reason is null or trim(p_reason) is null or length(p_reason)>1000 then
      raise_application_error(-20004,'A review reason of 1 to 1000 characters is required'); end if;
    if r.state='BLOCKED' then raise_application_error(-20008,'Review request is blocked'); end if;
    if r.state='PENDING' and r.expires_at<=systimestamp then
      raise_application_error(-20008,'Review request expired; request a new email'); end if;
    if p_code is null or p_code<>'6004' then
      update XXAF_RNW_EMAIL_REQUESTS set attempts=attempts+1,
        state=case when attempts+1>=5 then 'BLOCKED' else state end where draft_id=p_draft_id and state='PENDING';
      audit_event(p_draft_id,s.user_id,'EMAIL_CODE_DENIED','Incorrect demo code; code not logged');
      clear_context; commit; raise_application_error(-20008,'Incorrect demo approval code');
    end if;
    if r.state='APPROVED' then
      select * into v from XXAF_RNW_REVIEWS where draft_id=p_draft_id;
      if v.draft_hash<>d.draft_hash or v.review_reason<>trim(p_reason) then
        raise_application_error(-20008,'A different decision was already recorded'); end if;
      -- Retry returns the original receipt without extending or recreating approval.
    else
      if d.status<>'VALIDATED' then raise_application_error(-20008,'Only a validated draft can be reviewed'); end if;
      insert into XXAF_RNW_REVIEWS(draft_id,draft_hash,reviewer,review_reason,expires_at)
        values(p_draft_id,d.draft_hash,substr('DEMO_EMAIL:'||v_email,1,128),trim(p_reason),systimestamp+interval '1' hour);
      update XXAF_RNW_DRAFTS set status='REVIEWED',updated_at=systimestamp where draft_id=p_draft_id;
      update XXAF_RNW_EMAIL_REQUESTS set state='APPROVED' where draft_id=p_draft_id;
      audit_event(p_draft_id,s.user_id,'EMAIL_DEMO_REVIEWED','Recipient: '||v_email||'; reason: '||trim(p_reason));
      select * into v from XXAF_RNW_REVIEWS where draft_id=p_draft_id;
    end if;
    select json_object('draft_id' value d.draft_id,'draft_hash' value d.draft_hash,
      'status' value 'REVIEWED','review_mode' value 'FIXED_CODE_DEMO',
      'recipient' value v_email,'review_reason' value v.review_reason,
      'expires_at' value to_char(v.expires_at,'YYYY-MM-DD HH24:MI:SS'),
      'review_current' value case when v.expires_at>systimestamp and v.consumed_at is null then 'true' else 'false' end format json,
      'import_submitted' value case when d.request_id is null then 'false' else 'true' end format json
      returning clob) into result from dual;
    clear_context; commit; return result;
  exception when others then rollback; clear_context; rollback; raise;
  end;
end XXAF_RENEWAL_EMAIL;
/
grant execute on XXAF_RENEWAL_EMAIL to AF_EBS_RENEWAL;
-- BEGIN DBA WRAPPERS PHASE (connect as the PDB DBA)
alter session set current_schema=SYS;
create or replace function AF_EBS_RENEWAL.RNW_REQUEST_EMAIL_REVIEW(
  p_draft_id number,p_expected_hash varchar2,p_recipient varchar2) return clob authid definer as r clob;
begin
  execute immediate 'begin :r := APPS.XXAF_RENEWAL_EMAIL.request_review(:id,:hash,:email); end;'
    using out r,in p_draft_id,in p_expected_hash,in p_recipient;
  return r;
end;
/
create or replace function AF_EBS_RENEWAL.RNW_CONFIRM_EMAIL_REVIEW(
  p_draft_id number,p_expected_hash varchar2,p_recipient varchar2,
  p_code varchar2,p_reason varchar2) return clob authid definer as r clob;
begin
  execute immediate 'begin :r := APPS.XXAF_RENEWAL_EMAIL.confirm_review(:id,:hash,:email,:code,:reason); end;'
    using out r,in p_draft_id,in p_expected_hash,in p_recipient,in p_code,in p_reason;
  return r;
end;
/
declare n number;
begin
  select count(*) into n from dba_errors where
    (owner='APPS' and name='XXAF_RENEWAL_EMAIL') or
    (owner='AF_EBS_RENEWAL' and name in ('RNW_REQUEST_EMAIL_REVIEW','RNW_CONFIRM_EMAIL_REVIEW'));
  if n<>0 then raise_application_error(-20099,'Email review compilation failed; inspect DBA_ERRORS'); end if;
end;
/
