#!/usr/bin/env python

# Load libraries
import numpy as np
import psycopg2
import sys, os
import string
from optparse import OptionParser

def buildDsn(dbname, **kwargs):
    # Function to build dsn string for psycopg2 connections
    dsn = 'dbname=%s' % dbname

    for key in kwargs:
        if kwargs[key] is not None:
            dsn += " %s=%s" % (key, kwargs[key])

    return dsn

def parseSqlToCmds(sqlTxt):
    '''
    Function parse SQL text (as list of lines) into commands.

    Removes comment-only lines and splits based upon semicolons.

    Returns list of command strings.
    '''
    # Remove comments
    sqlTxt = [line.strip('\n\r') for line in sqlTxt if line[0:2]!='--']
    sqlTxt = [line.split('--')[0] for line in sqlTxt]

    # Merge into a single string
    sqlTxt = ''.join(sqlTxt)

    # Split into commands based upon semicolons
    sqlCmds = sqlTxt.split(';')
    sqlCmds = [s for s in sqlCmds if len(s) > 0]
    
    # Add semicolons back to end of commands
    sqlCmds = [s + ';' for s in sqlCmds]

    return(sqlCmds)

def setupDatabase(schemaName, schemaFile, opts, verbose=1):
    '''
    Function to coordinate setup of database based on given schema
    '''
    
    # First, load schema into memory
    schemaTxt = schemaFile.readlines()

    # Parse into commands
    schemaCmds = parseSqlToCmds(schemaTxt)
    
    # Substitute desired schema name for placeholder
    schemaCmds = [string.replace(s, opts.var, schemaName) for s in schemaCmds]

    # Connect to database
    dsn = buildDsn(opts.dbname, user=opts.user, host=opts.host)
    if verbose:
        print >> sys.stderr, "DSN:\t", dsn
    conn = psycopg2.connect(dsn)

    # Execute commands
    cur = conn.cursor()

    for cmd in schemaCmds:
        if verbose:
            print >> sys.stderr, cmd
        cur.execute(cmd)

    # Commit changes
    conn.commit()

    # Close connection
    cur.close()
    conn.close()


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
    parser.add_option('--var', dest='var',
                      default='TEMPLATE',
                      help='Placeholder to replace in schema SQL file')

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
    setupDatabase(schemaName, schemaFile, opts)

    return 0


# Run main if called (rather than imported)
if __name__ == '__main__':
    main(sys.argv[1:])
