import sqlite3 as sqlite
import json
import time
import os
import datetime
from cache_handler import *
from nasa_secrets import *


dir_path = os.path.dirname(os.path.realpath(__file__))
DBNAME = ('{}/{}').format(dir_path, 'nasa.db')
SOLAR_FLARE_URL = 'https://api.nasa.gov/DONKI/FLR'
CME_URL = 'https://api.nasa.gov/DONKI/CMEAnalysis'
PARTICLE_URL = 'https://api.nasa.gov/DONKI/SEP'
NEO_URL = 'https://api.nasa.gov/neo/rest/v1/feed'



#####################################################
# CREATE THE TABLES
# function also deletes tables if they already exist
#####################################################
def create_tables():
    # Connect to database
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    statement = "DROP TABLE IF EXISTS 'SolarFlares';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'SolarFlareInstruments';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'SolarFlareTypes';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'CME';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'WikiScrapes';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'SolarEnergeticParticles';"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'NearEarthObjects';"
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'SolarFlares' (
            'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
            'FlareID' TEXT,
            'Start' TEXT,
            'End' TEXT,
            'PeakTime' TEXT NOT NULL,
            'RegionNum' INTEGER,
            'Type' TEXT NOT NULL,
            'Location' TEXT,
            'LinkedEventID' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'SolarFlareInstruments' (
            'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
            'InstrumentID' INTEGER,
            'Name' TEXT,
            'SolarFlareID' INTEGER,
            FOREIGN KEY('SolarFlareID') REFERENCES SolarFlares(ID)
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'SolarFlareTypes' (
            'Type' TEXT PRIMARY KEY,
            'XrayOutput' REAL,
            FOREIGN KEY ('Type') REFERENCES SolarFlares(Type)
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'CME' (
            'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
            'CMEID' TEXT,
            'Note' TEXT,
            'Time' TEXT,
            'Type' TEXT,
            'Angle' REAL,
            'Speed' REAL,
            'Latitude' REAL,
            'Longitude' REAL,
            FOREIGN KEY('CMEID') REFERENCES SolarFlares(LinkedEventID)
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'WikiScrapes' (
            'ID' TEXT PRIMARY KEY,
            'Link' TEXT,
            'Text' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()


    statement = '''
        CREATE TABLE 'SolarEnergeticParticles' (
            'ID' TEXT PRIMARY KEY,
            'Date' TEXT,
            'SolarFlareID' TEXT,
            'CMEID' TEXT,
            'Instruments' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'NearEarthObjects' (
            'ID' NUMBER PRIMARY KEY,
            'Date' TEXT,
            'Name' TEXT,
            'Diameter' REAL,
            'Hazardous' INTEGER,
            'ClosestApproach' REAL
        );
    '''
    cur.execute(statement)
    conn.commit()



#####################################################
# POPULATE THE SOLAR ENERGETIC PARTICLES TABLE
# function also shows progress bar
#####################################################
def populate_particle_table(particleFile):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"ID", "Date", "SolarFlareID", "CMEID", "Instruments"'

    count = 0
    for particle in particleFile:

        count += 1
        if count % 25 == 0:
            print('#', end='', flush=True)
            time.sleep(1)

        flareID = ''
        cmeID = ''
        instruments = ''

        if particle['linkedEvents']:
            for event in particle['linkedEvents']:
                if len(event['activityID'].split('FLR')) > 1:
                    flareID += event['activityID'] + ','
                if len(event['activityID'].split('CME')) > 1:
                    cmeID += event['activityID'] + ','

        if particle['instruments']:
            for instrument in particle['instruments']:
                instruments += instrument['displayName'] + ','


        sql = 'INSERT INTO SolarEnergeticParticles(' + clms + ') VALUES (?, ?, ?, ?, ?)'
        cur.execute(sql, 
            (particle['sepID'], (particle['eventTime'].split('T')[0]).split('-')[0], flareID[:(len(flareID)-1)],
             cmeID[:(len(cmeID)-1)], instruments[:(len(instruments)-1)])
        )
    # commit and close changes
    conn.commit()
    conn.close()



#####################################################
# POPULATE THE NESR ESRTH OBJECTS TABLE
# function also shows progress bar
#####################################################
def populate_neo_table(neoFile):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = "'ID', 'Date', 'Name', 'Diameter', 'Hazardous', 'ClosestApproach'"

    count = 0
    for date in neoFile['near_earth_objects']:
        for neo in neoFile['near_earth_objects'][date]:

            count += 1
            if count % 25 == 0:
                print('#', end='', flush=True)
                time.sleep(1)


            hazardous = 0
            if neo['is_potentially_hazardous_asteroid']:
                hazardous = 1

            sql = 'INSERT INTO NearEarthObjects(' + clms + ') VALUES (?, ?, ?, ?, ?, ?)'
            cur.execute(sql, 
                (neo['id'],
                 date,
                 neo['name'],
                 neo['estimated_diameter']['kilometers']['estimated_diameter_max'],
                 hazardous,
                 neo['close_approach_data'][0]['miss_distance']['kilometers']
                )
            )
    conn.commit()
    conn.close()




#####################################################
# POPULATE THE SOLAR FLARES TABLE
# function also shows progress bar
#####################################################
def populate_flares_table(jsonFile):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"FlareID", "Start", "End", "PeakTime", "RegionNum", "Type", "Location", "LinkedEventID"'

    count = 0
    for flare in jsonFile:

        count += 1
        if count % 25 == 0:
            print('#', end='', flush=True)
            time.sleep(1)

        sql = 'INSERT INTO SolarFlares(' + clms + ') VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        linkedEvent = 'None'
        if flare['linkedEvents']:
            linkedEvent = flare['linkedEvents'][0]['activityID']

        cur.execute(sql, 
            (flare['flrID'], flare['beginTime'], flare['endTime'], flare['peakTime'], 
             flare['activeRegionNum'], flare['classType'], flare['sourceLocation'], linkedEvent)
        )
    # commit and close changes
    conn.commit()
    conn.close()
 


#####################################################
# POPULATE THE WKI SCRAPES TABLE
#####################################################
def populate_wikiscrapes_table(objArr):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"ID", "Link", "Text"'

    for obj in objArr:
        sql = 'INSERT INTO WikiScrapes(' + clms + ') VALUES (?, ?, ?)'
        cur.execute(sql, (obj['id'], obj['link'], obj['text']))
    # commit and close changes
    conn.commit()
    conn.close()



#####################################################
# POPULATE THE SOLAR FLARE INSTRUMENTS TABLE
# function also shows progress bar
#####################################################
def populate_flares_instrument_table(jsonFile):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"InstrumentID", "Name", "SolarFlareID"'
    index = 0
    for flare in jsonFile:
        index += 1
        if index % 25 == 0:
            print('#', end='', flush=True)
            time.sleep(1)

        for instrument in flare['instruments']:

            sql = 'INSERT INTO SolarFlareInstruments(' + clms + ') VALUES (?, ?, ?)'
            cur.execute(sql, 
                (instrument['id'], instrument['displayName'], index)
            )
    # commit and close changes
    conn.commit()
    conn.close()



#####################################################
# POPULATE THE SOLAR FLARE TYPES TABLE
# function also shows progress bar
#####################################################
def populate_flare_types_table():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"Type", "XrayOutput"'
    
    energies = {
        'B': 1e-7,
        'C': 1e-6,
        'M': 1e-5,
        'X': 1e-4,
    }

    sql = '''
        SELECT DISTINCT TYPE
        FROM SolarFlares 
    '''

    types = cur.execute(sql).fetchall()

    index = 0
    for sType in types:
        index += 1
        if index % 10 == 0:
            print('#', end='', flush=True)
            time.sleep(1)

        sClass = sType[0][0]
        multiplier = float(sType[0][1:])
        energy = multiplier * energies[sClass]

        sql = 'INSERT INTO SolarFlareTypes(' + clms + ') VALUES (?, ?)'
        cur.execute(sql, (sType[0], energy))
    # commit and close changes
    conn.commit()
    conn.close()



#####################################################
# POPULATE THE CME TABLE
# function also shows progress bar
#####################################################
def populate_cme_table(cmeFile):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    clms = '"CMEID", "Note", "Time", "Type", "Angle", "Speed", "Latitude", "Longitude"'
        
    sql = '''
        SELECT LinkedEventID
        FROM SolarFlares 
    '''
    events = cur.execute(sql).fetchall()
    
    count = 0
    for event in events:
        count += 1
        if count % 25 == 0:
            print('#', end='', flush=True)
            time.sleep(1)
        for cme in cmeFile:
            if event[0] == cme['associatedCMEID']:

                sql = 'INSERT INTO CME(' + clms + ') VALUES (?, ?, ?, ?, ?, ?, ? ,?)'
                cur.execute(sql, 
                    (cme['associatedCMEID'], cme['note'], cme['time21_5'], cme['type'],
                     cme['halfAngle'], cme['speed'], cme['latitude'], cme['longitude'])
                )
    # commit and close changes
    conn.commit()
    conn.close()


#####################################################
# MAIN FUNCTION TO POPULATE NASA.DB
# function creates user friendly ouput to the
# terminal showing the progress of building the
# database.
#####################################################
def populate_db():

    print('\n', '**POPULATE DATABASE**', '\n')

    create_tables()

    params = {
        'startDate': '2008-11-22',
        'endDate': str(datetime.now()).split()[0],
        'api_key': NASA_API,
    }

    print('GETTING Solar Flare DATA... ... ...')
    flr_file = getData(SOLAR_FLARE_URL, params, 'solar-flare.json')

    print('CREATING FLARES TABLE: in progress... ...', flush=True)
    populate_flares_table(flr_file)
    print(' FLARES TABLE: complete\n')

    print('CREATING FLARE INSTRUMENTS TABLE: in progress... ...', flush=True)
    populate_flares_instrument_table(flr_file)
    print(' FLARE INSTRUMENTS TABLE: complete\n')

    print('CREATING FLARE TYPES TABLE: in progress... ...', flush=True)
    populate_flare_types_table()
    print(' FLARE TYPES TABLE: complete\n')

    print('GETTING CME DATA... ... ...')
    cme_file = getData(CME_URL, params, 'cme.json')

    print('CREATING CME TABLE: in progress... ...')
    populate_cme_table(cme_file)
    print('#', end='')
    print(' CME TABLE: complete\n')


    print('GETTING Particle DATA... ... ...')
    particle_file = getData(PARTICLE_URL, params, 'particle.json')

    print('CREATING Particle TABLE: in progress... ...')
    populate_particle_table(particle_file)
    print('#', end='')
    print(' PARTICLE TABLE: complete\n')


    print('GETTING Near Earth Objects DATA... ... ...')
    neo_file = getData(NEO_URL, params, 'neo.json')

    print('CREATING Near Earth Objects TABLE: in progress... ...')
    populate_neo_table(neo_file)
    print('#', end='')
    print(' Near Earth Objects TABLE: complete\n')



    print('GETTING Scrapes FROM WIKIPEDIA... ... ...')
    wikiScrapes = [
        {'id': 'flare', 'link': 'https://en.wikipedia.org/wiki/Solar_flare', 'text': '', 'file': 'solar-flare-wiki.json'},
        {'id': 'cme', 'link': 'https://en.wikipedia.org/wiki/Coronal_mass_ejection', 'text': '', 'file': 'cme-wiki.json'},
        {'id': 'particle', 'link': 'https://en.wikipedia.org/wiki/Solar_energetic_particles','text': '', 'file': 'particle-wiki.json'},
        {'id': 'neo', 'link': 'https://en.wikipedia.org/wiki/Near-Earth_object','text': '', 'file': 'neo-wiki.json'}
    ]
    for scrape in wikiScrapes:
        scrape['text'] = getData(scrape['link'], {'type': scrape['id']}, scrape['file'], True)

    print('CREATE WIKI SCRAPES TABLE: in progress... ...')
    populate_wikiscrapes_table(wikiScrapes)
    print(' WIKI SCRAPES TABLE: complete\n')





    print('\n**DATABASE COMPLETE**')
    print('==========================================================\n')


# Run this file terminal output
populate_db()
