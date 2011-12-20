A database system for MSMS quantitation
=======================================

This contains the schema, scripts, and associated tests for a PostgreSQL
database system for MSMS proteomics data. It is intended to hold data that has
already been identified and had chromatographic intensity integrated over time
(i.e. data processed by MaxQuant).

The system will handle data IO, storage, retrieval, and management for the
entire inference process. It will handle both the raw data and all MCMC output,
allowing for easy and efficient analysis of posterior samples.

