#!/usr/bin/env python

# Load libraries
import numpy as np
import psycopg2
import sys, os
import tempfile
import StringIO
import csv
from optparse import OptionParser

def loadToDatabase(dataFile, opts):
    '''
    Function to coordinate loading of data from dataFile into a PostgreSQL
    database
    '''
    
    # First, format the data as needed
    # Breaking into five components:
    #   - Peptides with numeric (ordered) identifiers
    #   - Proteins with numeric (ordered) identifiers
    #   - Peptide to protein mapping (paired numeric identifiers)
    #   - Experiments with numeric (ordered) identifiers
    #   - Observations with numeric identifiers for peptides, proteins, and
    #     experiments

    # Keeping identifiers and peptide to protein mapping in memory,
    # working with the observations (intensity etc.) via temporary file(s)

    # 


def main(argv):
    '''
    Function to parse arguments and manage execution

    argv should be sys.argv[1:] or equivalently formatted
    '''
    # Setup option parser
    parser = OptionParser()

    parser.add_option('-u', '--user', dest='user',
                      default=None, metavar='USER',
                      help='User for PostgreSQL database')
    parser.add_option('--host', dest='host',
                      default=None,
                      help='Host for database; defaults to UNIX socket')
    parser.add_option('-d', '--dbname', dest='dbname',
                      default='proteome', metavar='DBNAME',
                      help='Name of database to load data into')

    # Parse arguments
    opts, args = parser.parse_args(argv)
    
    # Get data filename
    if len(args)>0:
        dataFilename    = args[0]
        dataFile        = open(dataFilename, 'rb')
    else:
        dataFile        = sys.stdin
    
    # Call function to load data into database
    loadToDatabase(dataFile, opts)

    return 0


# Run main if called (rather than imported)
if __name__ == '__main__':
    main(sys.argv[1:])
