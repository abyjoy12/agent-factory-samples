-- Run as the EBS PDB DBA, once, during an approved customization window.
-- Deliberately fails if this schema already exists; never drops existing data.
whenever sqlerror exit failure rollback
set define off
create user XXAF_RENEWAL no authentication
  default tablespace APPS_TS_TX_DATA quota 100M on APPS_TS_TX_DATA account lock;
alter user XXAF_RENEWAL enable editions;

create table XXAF_RENEWAL.XXAF_RNW_SCOPE (
  db_username varchar2(128) primary key,
  user_id number not null, responsibility_id number not null,
  application_id number not null, org_id number not null,
  source_header_id number not null, enabled_flag varchar2(1) default 'Y' not null,
  constraint XXAF_RNW_SCOPE_C check (enabled_flag in ('Y','N'))
);
create table XXAF_RENEWAL.XXAF_RNW_DRAFTS (
  draft_id number primary key, db_username varchar2(128) not null,
  idempotency_key varchar2(100) not null,
  source_header_id number not null, source_revision number not null,
  org_id number not null, source_snapshot clob not null,
  source_hash varchar2(64) not null, draft_hash varchar2(64) not null,
  start_date date not null, end_date date not null,
  uplift_pct number not null, evidence_ref varchar2(1000) not null,
  status varchar2(30) default 'STAGED' not null,
  created_by number not null, created_at timestamp default systimestamp not null,
  updated_at timestamp default systimestamp not null,
  interface_header_id number, batch_id number, request_id number,
  result_header_id number, result_number varchar2(25), result_status varchar2(25),
  constraint XXAF_RNW_DRAFT_KEY unique(db_username,idempotency_key),
  constraint XXAF_RNW_DRAFT_STATE check(status in
    ('STAGED','VALIDATED','REVIEWED','SUBMITTED','IMPORTED','IMPORT_FAILED')),
  constraint XXAF_RNW_DRAFT_PRICE check(uplift_pct between 0 and 10),
  constraint XXAF_RNW_DRAFT_DATES check(end_date >= start_date and end_date < start_date+366)
);
create table XXAF_RENEWAL.XXAF_RNW_LINES (
  draft_id number not null, source_line_id number not null, line_num number not null,
  line_type_id number not null, item_id number not null, category_id number not null,
  item_description varchar2(240), unit_of_measure varchar2(25) not null,
  old_price number not null, new_price number not null,
  constraint XXAF_RNW_LINES_PK primary key(draft_id,line_num)
);
create table XXAF_RENEWAL.XXAF_RNW_REVIEWS (
  draft_id number primary key, draft_hash varchar2(64) not null,
  reviewer varchar2(128) not null, review_reason varchar2(1000) not null,
  reviewed_at timestamp default systimestamp not null,
  expires_at timestamp not null, consumed_at timestamp
);
create table XXAF_RENEWAL.XXAF_RNW_AUDIT (
  audit_id number primary key, draft_id number not null,
  db_username varchar2(128) not null, user_id number,
  event_name varchar2(30) not null, event_detail varchar2(1000),
  created_at timestamp default systimestamp not null
);
create sequence XXAF_RENEWAL.XXAF_RNW_S nocache;
grant select,insert,update,delete on XXAF_RENEWAL.XXAF_RNW_SCOPE to APPS;
grant select,insert,update,delete on XXAF_RENEWAL.XXAF_RNW_DRAFTS to APPS;
grant select,insert,update,delete on XXAF_RENEWAL.XXAF_RNW_LINES to APPS;
grant select,insert,update,delete on XXAF_RENEWAL.XXAF_RNW_REVIEWS to APPS;
grant select,insert,update,delete on XXAF_RENEWAL.XXAF_RNW_AUDIT to APPS;
grant select on XXAF_RENEWAL.XXAF_RNW_S to APPS;
