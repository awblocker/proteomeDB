-- Setting up empty schema as TEMPLATE for study-specific schema within database
CREATE SCHEMA TEMPLATE;
SET search_path to TEMPLATE,public;

-- Table for protein information, no peptides
CREATE TABLE TEMPLATE.proteins (
    protein_id      bigserial primary key,
    protein_name    varchar(100) unique
);

-- Table for peptide information, unique by sequence
-- Protein mapping is in a separate table
CREATE TABLE TEMPLATE.peptides (
    peptide_id      bigserial primary key,
    peptide_seq     varchar(100) unique
);

-- Table for protein to peptide mapping
-- Enforcing non-unique foreign key relationship
CREATE TABLE TEMPLATE.peptide_to_protein (
    protein_id      bigint references TEMPLATE.proteins,
    peptide_id      bigint references TEMPLATE.peptides
);

-- Table for experiment data
CREATE TABLE TEMPLATE.experiments (
    experiment_id   bigserial primary key,
    experiment_name varchar(100)
);

-- Table for observed intensities and MSMS counts
CREATE TABLE TEMPLATE.observations (
    obs_id          bigserial primary key,
    experiment_id   bigint references TEMPLATE.experiments,
    peptide_id      bigint references TEMPLATE.peptides,
    intensity       double precision,
    msms_count      int
);

-- Note: Probably want to remove then reactivate foreign key restrictions
--       on initial data load
