-- ADB-S DBA installation, once, after verifying the intended target.
-- This file contains no runtime credentials or business scope rows.
-- Create the separate AF_EBS_DOC_MCP login through approved secret provisioning.
whenever sqlerror exit failure rollback
set define off

create user AF_EBS_DOCS no authentication account lock
  default tablespace DATA quota 512M on DATA;
grant create mining model to AF_EBS_DOCS;
grant execute on SYS.DBMS_VECTOR to AF_EBS_DOCS;
grant execute on CTXSYS.DBMS_VECTOR_CHAIN to AF_EBS_DOCS;

create table AF_EBS_DOCS.RNW_DOC_SCOPE (
  DB_USERNAME varchar2(128) not null, SOURCE_HEADER_ID number not null,
  ORG_ID number not null, SUPPLIER_ID number not null, ACTIVE char(1) default 'Y' not null,
  constraint RNW_DOC_SCOPE_PK primary key (DB_USERNAME,SOURCE_HEADER_ID),
  constraint RNW_DOC_SCOPE_ACTIVE check (ACTIVE in ('Y','N')));

create table AF_EBS_DOCS.RNW_DOCUMENTS (
  DOCUMENT_KEY varchar2(100) primary key, DOCUMENT_ID number not null,
  ATTACHMENT_ID number not null, MEDIA_ID number not null,
  HEADER_ID number not null, BPA_NUMBER varchar2(100) not null, HEADER_REVISION number not null,
  ORG_ID number not null,SUPPLIER_ID number not null,
  FILENAME varchar2(255) not null,MIME_TYPE varchar2(100) not null,
  SHA256 varchar2(64) not null, SOURCE_METADATA clob check (SOURCE_METADATA is json),
  FILE_DATA blob not null, DOCUMENT_TEXT clob,
  CAPTURED_AT timestamp with time zone default systimestamp not null,
  ACTIVE char(1) default 'N' not null,
  constraint RNW_DOCUMENTS_ACTIVE check (ACTIVE in ('Y','N')));

create table AF_EBS_DOCS.RNW_CHUNKS (
  DOCUMENT_KEY varchar2(100) not null references AF_EBS_DOCS.RNW_DOCUMENTS(DOCUMENT_KEY),
  CHUNK_ID number not null, TEXT_OFFSET number not null,TEXT_LENGTH number not null,
  CHUNK_TEXT varchar2(4000) not null,EMBEDDING vector(384,float32) not null,
  constraint RNW_CHUNKS_PK primary key (DOCUMENT_KEY,CHUNK_ID));
