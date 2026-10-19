-- Read-only operator verification, as APPS. Keep operational output private.
set define off
set sqlformat csv
set feedback off
whenever sqlerror exit failure rollback
select object_name,object_type,status from user_objects
where object_name in ('XXAF_RENEWAL_API','XXAF_RENEWAL_ADMIN') order by object_name,object_type;
select oracle_username,enabled_flag,read_only_flag from fnd_oracle_userid
where oracle_username='XXAF_RENEWAL';
select draft_id,status,source_header_id,source_revision,org_id,start_date,end_date,
       uplift_pct,batch_id,request_id,result_header_id,result_number,result_status
from XXAF_RNW_DRAFTS order by draft_id;
select d.draft_id,r.request_id,r.phase_code,r.status_code,r.completion_text,
       r.argument2 document_type,r.argument4 create_items,r.argument5 create_sourcing_rules,
       r.argument6 import_status,r.argument8 batch_id,r.argument9 org_id
from XXAF_RNW_DRAFTS d join fnd_concurrent_requests r on r.request_id=d.request_id;
select d.draft_id,h.segment1,h.type_lookup_code,h.authorization_status,h.currency_code,
       h.agent_id,h.org_id,h.reference_num,h.comments,h.created_by,
       to_char(h.start_date,'YYYY-MM-DD HH24:MI:SS') start_date,
       to_char(h.end_date,'YYYY-MM-DD HH24:MI:SS') end_date,
       l.line_num,l.item_id,l.item_description,l.unit_price,l.unit_meas_lookup_code,
       to_char(l.expiration_date,'YYYY-MM-DD HH24:MI:SS') line_expiration
from XXAF_RNW_DRAFTS d join po_headers_all h on h.po_header_id=d.result_header_id
join po_lines_all l on l.po_header_id=h.po_header_id order by d.draft_id,l.line_num;
select audit_id,draft_id,db_username,event_name,event_detail,created_at
from XXAF_RNW_AUDIT order by audit_id;
