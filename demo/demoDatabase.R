# Load libraries
library(RPostgreSQL)
library(stringr)

# Connect to database
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="proteome")

# Pull entire dataset from view
dataset <- dbGetQuery(con, "select * from ups2.dataset")

# Get experiment information
experiments <- dbGetQuery(con,
                          str_c("select experiment_name, ",
                                "count(distinct peptide_seq) as npeptides, ",
                                "count(distinct protein_name) as nproteins",
                                " from ups2.dataset group by experiment_name")
                          )

# Get proportion of peptides observed for a single experiment
propIdent <- dbGetQuery(con,
                     str_c("select t.protein_name,",
                           "cast(sum(case when t.obs then 1 else 0 end) ",
                           "as float8)/count(t.peptide_seq) as prop_ident ",
                           "from (select peptide_seq, protein_name, ",
                           "(sum(intensity)>0) as obs from ups2.dataset where ",
                           "experiment_name = 'ups2_6h_1' ",
                           "group by peptide_seq, protein_name) as t ",
                           "group by protein_name")
                     )

