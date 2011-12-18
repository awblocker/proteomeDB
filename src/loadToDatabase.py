#!/usr/bin/env python

# Load libraries
import numpy as np
import psycopg2
import sys, os
import tempfile
import StringIO
import csv
import bisect
from optparse import OptionParser

# Set constants
SQL_DELIM = '\t'

# Define utility functions
def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError

def buildDsn(dbname, **kwargs):
    'Function to build dsn string for psycopg2 connections'
    dsn = 'dbname=%s' % dbname

    for key in kwargs:
        if kwargs[key] is not None:
            dsn += " %s=%s" % (key, kwargs[key])

    return dsn

def loadToDatabase(dataFile, opts, verbose=1):
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

    # First, scan through dataFile and accumulate unique proteins, peptides,
    # and experiments
    proteinsUniq    = set()
    peptidesUniq    = set()
    experimentsUniq = set()

    reader = csv.DictReader(dataFile, delimiter=opts.delim)
    for line in reader:
        proteinsUniq.add(line['protein'])
        peptidesUniq.add(line['peptide'])
        experimentsUniq.add(line['experiment'])

    proteinsUniq = list(proteinsUniq)
    proteinsUniq.sort()
    #
    peptidesUniq = list(peptidesUniq)
    peptidesUniq.sort()
    #
    experimentsUniq = list(experimentsUniq)
    experimentsUniq.sort()

    # Now, iterate through the file again, building the protein to peptide
    # mapping and constructing the temporary file of observation data
    obsTmp = tempfile.TemporaryFile()
    proteinToPep = set()

    dataFile.seek(0)
    dataFile.next()
    for line in reader:
        # Get observation information
        intensity = line['intensity']
        msmsCount = line['msms_count']
        
        # Get protein/peptide pair as indices
        proteinId = proteinsUniq.index(line['protein']) + 1
        peptideId = peptidesUniq.index(line['peptide']) + 1
        
        # Add pair to mapping
        proteinToPep.add( (str(proteinId), str(peptideId)) )

        # Get experiment ID
        experimentId = experimentsUniq.index(line['experiment']) + 1

        # Build line of observations file
        obsLine = SQL_DELIM.join((str(experimentId), str(peptideId),
                                  intensity, msmsCount))
        obsLine += '\n'
        
        if verbose > 1:
            print obsLine

        # Write line to temporary file
        obsTmp.write(obsLine)
    
    # Convert lists and sets to nicely-formatted strings for COPY FROM
    # operations
    experimentsStr  = '\n'.join(experimentsUniq)
    proteinsStr     = '\n'.join(proteinsUniq)
    peptidesStr     = '\n'.join(peptidesUniq)

    mappingStr      = '\n'.join([SQL_DELIM.join(pair) for pair in
                                 proteinToPep])

    # Connect to database
    dsn = buildDsn(opts.dbname, user=opts.user, host=opts.host)
    if verbose:
        print >> sys.stderr, "DSN:\t", dsn
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    # Add schema to search path
    cur.execute("SET search_path to %s,public;",
                (opts.schema,))

    # Fill tables; sequence matters!


    # Fill descriptor tables
    
    # Experiments
    cur.copy_from(StringIO.StringIO(experimentsStr), 'experiments',
                  columns=('experiment_name',))

    # Peptides
    cur.copy_from(StringIO.StringIO(peptidesStr), 'peptides',
                  columns=('peptide_seq',))
    
    # Proteins
    cur.copy_from(StringIO.StringIO(proteinsStr), 'proteins',
                  columns=('protein_name',))
    
    # Commit changes to descriptors
    conn.commit()
    

    # Fill mapping table

    # Drop foreign key constraints
    cur.execute('ALTER TABLE peptide_to_protein DROP CONSTRAINT "%s"' %
                ("peptide_to_protein_peptide_id_fkey",))
    cur.execute('ALTER TABLE peptide_to_protein DROP CONSTRAINT "%s"' %
                ("peptide_to_protein_protein_id_fkey",))
    
    # Copy data
    cur.copy_from(StringIO.StringIO(mappingStr), 'peptide_to_protein',
                  columns=('protein_id', 'peptide_id'))

    # Re-add foreign key constraints
    cur.execute(('ALTER TABLE peptide_to_protein ADD CONSTRAINT "%s"' +
                 'FOREIGN KEY (%s) references %s(%s) MATCH FULL') %
                ("peptide_to_protein_peptide_id_fkey", 'peptide_id',
                'peptides', 'peptide_id'))
    cur.execute(('ALTER TABLE peptide_to_protein ADD CONSTRAINT "%s"' +
                 'FOREIGN KEY (%s) references %s(%s) MATCH FULL') %
                ("peptide_to_protein_protein_id_fkey", 'protein_id',
                'proteins', 'protein_id'))

    # Commit changes to mapping
    conn.commit()


    # Fill observations table
    
    # Drop foreign key constraints
    cur.execute('ALTER TABLE observations DROP CONSTRAINT "%s"' %
                ("observations_experiment_id_fkey",))
    cur.execute('ALTER TABLE observations DROP CONSTRAINT "%s"' %
                ("observations_peptide_id_fkey",))
    
    # Copy data
    obsTmp.seek(0)
    cur.copy_from(obsTmp, 'observations',
                  columns=('experiment_id', 'peptide_id',
                           'intensity', 'msms_count'))

    # Re-add foreign key constraints
    cur.execute(('ALTER TABLE observations ADD CONSTRAINT "%s"' +
                 'FOREIGN KEY (%s) references %s(%s) MATCH FULL') %
                ("observations_experiment_id_fkey", 'experiment_id',
                'experiments', 'experiment_id'))
    cur.execute(('ALTER TABLE observations ADD CONSTRAINT "%s"' +
                 'FOREIGN KEY (%s) references %s(%s) MATCH FULL') %
                ("observations_peptide_id_fkey", 'peptide_id',
                'peptides', 'peptide_id'))

    # Commit observations fill
    conn.commit()


    # Close connection
    cur.close()
    conn.close()

    # Close temporary and data files
    obsTmp.close()
    dataFile.close()


    
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
    parser.add_option('--delim', dest='delim',
                      default='\t',
                      help='Delimiter for data file; defaults to tab')
    parser.add_option('--schema', dest='schema',
                      default='ups2',
                      help='Schema name to use; added to search path')

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
