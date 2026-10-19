-- Run as the EBS PDB DBA after creating/scoping AF_EBS_RENEWAL.
-- PAF discovers routines owned by CURRENT_SCHEMA. The runtime still receives
-- no CREATE PROCEDURE, table privileges, roles, or review-package access.
-- Fixed anonymous blocks bridge this noneditioned login to the editioned APPS
-- package without enabling editions on an integration login. All values bind;
-- no caller-controlled SQL or routine name is accepted.
whenever sqlerror exit failure rollback
set define off
create or replace function AF_EBS_RENEWAL.RNW_GET_BPA_SNAPSHOT(
    p_source_header_id number) return clob authid definer as
    l_result clob;
begin
    execute immediate
        'begin :r := APPS.XXAF_RENEWAL_API.get_bpa_snapshot(:id); end;'
        using out l_result, in p_source_header_id;
    return l_result;
end;
/
create or replace function AF_EBS_RENEWAL.RNW_STAGE_RENEWAL(
    p_source_header_id number, p_start_date varchar2, p_end_date varchar2,
    p_uplift_pct number, p_evidence_ref varchar2,
    p_idempotency_key varchar2) return clob authid definer as
    l_result clob;
begin
    execute immediate
        'begin :r := APPS.XXAF_RENEWAL_API.stage_renewal(:id,:s,:e,:u,:ref,:key); end;'
        using out l_result, in p_source_header_id, in p_start_date,
        in p_end_date, in p_uplift_pct, in p_evidence_ref, in p_idempotency_key;
    return l_result;
end;
/
create or replace function AF_EBS_RENEWAL.RNW_VALIDATE_RENEWAL(
    p_draft_id number) return clob authid definer as
    l_result clob;
begin
    execute immediate
        'begin :r := APPS.XXAF_RENEWAL_API.validate_renewal(:id); end;'
        using out l_result, in p_draft_id;
    return l_result;
end;
/
create or replace function AF_EBS_RENEWAL.RNW_SUBMIT_REVIEWED_RENEWAL(
    p_draft_id number) return clob authid definer as
    l_result clob;
begin
    execute immediate
        'begin :r := APPS.XXAF_RENEWAL_API.submit_reviewed_renewal(:id); end;'
        using out l_result, in p_draft_id;
    return l_result;
end;
/
create or replace function AF_EBS_RENEWAL.RNW_GET_RENEWAL_STATUS(
    p_draft_id number) return clob authid definer as
    l_result clob;
begin
    execute immediate
        'begin :r := APPS.XXAF_RENEWAL_API.get_renewal_status(:id); end;'
        using out l_result, in p_draft_id;
    return l_result;
end;
/
declare
    l_errors number;
    l_objects number;
begin
    select count(*) into l_errors from dba_errors
    where owner='AF_EBS_RENEWAL' and name in (
        'RNW_GET_BPA_SNAPSHOT','RNW_STAGE_RENEWAL','RNW_VALIDATE_RENEWAL',
        'RNW_SUBMIT_REVIEWED_RENEWAL','RNW_GET_RENEWAL_STATUS');
    select count(*) into l_objects from dba_objects
    where owner='AF_EBS_RENEWAL' and object_type='FUNCTION' and status='VALID'
      and object_name in ('RNW_GET_BPA_SNAPSHOT','RNW_STAGE_RENEWAL',
        'RNW_VALIDATE_RENEWAL','RNW_SUBMIT_REVIEWED_RENEWAL',
        'RNW_GET_RENEWAL_STATUS');
    if l_errors<>0 or l_objects<>5 then
        raise_application_error(-20020,'PAF renewal wrapper compilation failed');
    end if;
end;
/
