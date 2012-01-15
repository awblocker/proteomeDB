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
    msms_count      int CHECK (msms_count > 0) --Only contains observed peptides
);

-- View for peptides with protein annotations
CREATE VIEW TEMPLATE.annotated_peptides AS
    SELECT a.peptide_id, peptide_seq, a.protein_id, protein_name
    FROM TEMPLATE.peptide_to_protein AS a INNER JOIN
    TEMPLATE.proteins AS b ON a.protein_id = b.protein_id INNER JOIN
    TEMPLATE.peptides AS c ON a.peptide_id = c.peptide_id;

-- View for all proteins identified in each experiment
CREATE VIEW TEMPLATE.proteins_by_experiment AS
    SELECT DISTINCT obs.experiment_id, pep.protein_id, pep.protein_name
    FROM TEMPLATE.observations as obs INNER JOIN
    TEMPLATE.annotated_peptides as pep ON
    obs.peptide_id = pep.peptide_id;

-- View for all peptides from proteins identified in each experiment
CREATE VIEW TEMPLATE.peptides_by_experiment AS
    SELECT DISTINCT prot.experiment_id, prot.protein_id, prot.protein_name,
    pep.peptide_id, pep.peptide_seq
    FROM TEMPLATE.proteins_by_experiment as prot JOIN
    TEMPLATE.annotated_peptides as pep ON
    prot.protein_id = pep.protein_id;

-- View for dataset of all observed peptides with annotations
CREATE VIEW TEMPLATE.obs_dataset AS
    SELECT obs_id, experiment_name, peptide_seq, protein_name,
    intensity, msms_count
    FROM TEMPLATE.observations AS a JOIN TEMPLATE.annotated_peptides AS b
    ON a.peptide_id = b.peptide_id JOIN
    TEMPLATE.experiments AS c ON a.experiment_id = c.experiment_id
    ORDER BY a.experiment_id, protein_id, a.peptide_id;

-- View for dataset of all peptides for all experiments; returning NULLs for
-- those with 0 MSMS counts
CREATE VIEW TEMPLATE.dataset AS
    SELECT obs_id, experiment_name, peptide_seq, protein_name,
    intensity, COALESCE(msms_count, 0) AS msms_count
    FROM (TEMPLATE.observations AS obs RIGHT OUTER JOIN
    TEMPLATE.peptides_by_experiment AS pep ON obs.peptide_id = pep.peptide_id
    AND obs.experiment_id = pep.experiment_id) JOIN
    TEMPLATE.experiments AS exp ON pep.experiment_id = exp.experiment_id
    ORDER BY obs.experiment_id, protein_id, obs.peptide_id;

-- Note: Probably want to remove then reactivate foreign key restrictions
--       on initial data load
