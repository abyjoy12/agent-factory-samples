-- Run as APPS in the run edition after 01-schema.sql.
whenever sqlerror exit failure rollback
set define off
begin
  fnd_oracle_user_pkg.load_row('XXAF_RENEWAL','CUSTOM','INVALID',
    'Controlled BPA renewal staging','N','B');
  commit;
  ad_zd_table.upgrade('XXAF_RENEWAL','XXAF_RNW_SCOPE');
  ad_zd_table.upgrade('XXAF_RENEWAL','XXAF_RNW_DRAFTS');
  ad_zd_table.upgrade('XXAF_RENEWAL','XXAF_RNW_LINES');
  ad_zd_table.upgrade('XXAF_RENEWAL','XXAF_RNW_REVIEWS');
  ad_zd_table.upgrade('XXAF_RENEWAL','XXAF_RNW_AUDIT');
end;
/
create or replace synonym XXAF_RNW_S for XXAF_RENEWAL.XXAF_RNW_S;
