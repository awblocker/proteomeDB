#!/usr/bin/env python

# Load libraries
import numpy as np
import psycopg2
import sys, os
import tempfile
import StringIO
import csv
from optparse import OptionParser

def setupDatabase(schemaName, schemaFile, opts):
    '''
    Function to coordinate setup of database based on given schema
    '''
    
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
                      help='Name of database to setup schema in')

    # Parse arguments
    opts, args = parser.parse_args(argv)
    
    # Get data filename
    if len(args)>1:
        schemaName      = args[0]
        schemaFilename  = args[1]
        schemaFile      = open(schemaFilename, 'rb')
    else:
        print >> sys.stderr, 'Error -- Need schema name and file'
    
    # Call function to setup database
    setupDatabase(dataFile, opts)

    return 0


# Run main if called (rather than imported)
if __name__ == '__main__':
    main(sys.argv[1:])
