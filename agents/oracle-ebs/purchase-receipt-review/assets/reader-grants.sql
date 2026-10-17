-- Setup reference only: these SELECT grants already existed in the validated environment.
-- Execute as the view owner in the correct application PDB on a new installation.
-- No system ANY privilege, DML grant, role, or WITH GRANT OPTION is required.
GRANT SELECT ON APPS.XXAF_SCM_PURCHASE_ORDERS_V TO AF_EBS_SCM_RO;
-- No rollback is supplied for pre-existing grants: do not revoke shared-reader access blindly.
