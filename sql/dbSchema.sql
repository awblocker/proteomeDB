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
    pair_id         bigserial primary key,
    protein_id      bigint references TEMPLATE.proteins,
    peptide_id      bigint references TEMPLATE.peptides,
    CONSTRAINT unique_mapping UNIQUE (protein_id, peptide_id)
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

CREATE VIEW TEMPLATE.annotated_peptides AS
    SELECT a.peptide_id, peptide_seq, a.protein_id, protein_name
    FROM TEMPLATE.peptide_to_protein AS a LEFT JOIN
    TEMPLATE.proteins AS b ON a.protein_id = b.protein_id LEFT JOIN
    TEMPLATE.peptides AS c ON a.peptide_id = c.peptide_id;

CREATE VIEW TEMPLATE.dataset AS
    SELECT obs_id, experiment_name, peptide_seq, protein_name,
    intensity, msms_count
    FROM TEMPLATE.observations AS a LEFT JOIN TEMPLATE.annotated_peptides AS b
    ON a.peptide_id = b.peptide_id LEFT JOIN
    TEMPLATE.experiments AS c ON a.experiment_id = c.experiment_id
    ORDER BY a.experiment_id, protein_id, a.peptide_id;

-- Note: Probably want to remove then reactivate foreign key restrictions
--       on initial data load
