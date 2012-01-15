#! /bin/bash

# Test script for database setup scripts
dropdb proteome 
createdb proteome
python src/setupDatabase.py --dbname=proteome ups2 sql/dbSchema.sql
python src/loadToDatabase.py data/dataset.txt 
