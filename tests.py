import unittest
import sqlite3
from plots.flare import *
from plots.cme import *
from plots.neo import *
from plots.particle import *

DBNAME='./database/nasa.db'



class TestDatabase(unittest.TestCase):

    def test_flares_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT S.Start, S.Type, T.XrayOutput, I.Name
            FROM SolarFlares AS S
            JOIN SolarFlareTypes As T ON T.Type=S.Type
            JOIN SolarFlareInstruments AS I ON I.SolarFlareID=S.ID
            ORDER BY S.Start
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list[0]), 4)
        conn.close()

    def test_cme_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT C.Longitude, C.Latitude, C.Speed, C.Note, C.Type, C.Time, F.Type
            FROM CME AS C
            JOIN SolarFlares As F ON F.LinkedEventID=C.CMEID
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list[0]), 7)
        conn.close()

    def test_particle_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT P.Date, P.ID, COUNT(*)
            FROM SolarEnergeticParticles AS P
            GROUP BY P.Date
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list[0]), 3)
        conn.close()

    def test_neo_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Diameter, ClosestApproach, Hazardous, Name
            FROM NearEarthObjects
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list[0]), 4)
        conn.close()


class TestPlots(unittest.TestCase):

    def test_neo_plot(self):
        neoInst = NEO()
        a, b = neoInst.getData()
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertNotEqual(len(a['dist']), len(b['dist']))
        div = neoInst.makePlot()
        self.assertIsNotNone(div)

    def test_flare_plot(self):
        flareInst = SolarFlares()
        a = flareInst.getData()
        self.assertIsNotNone(a)
        self.assertEqual(len(a['y']), len(a['class']))
        div = flareInst.makePlot()
        self.assertIsNotNone(div)

    def test_cme_plot(self):
        cmeInst = CME()
        a = cmeInst.getData()
        self.assertIsNotNone(a)
        self.assertEqual(len(a['speed']), len(a['long']))
        div = cmeInst.makePlot()
        self.assertIsNotNone(div)

    def test_paricle_plot(self):
        paricleInst = SESE()
        a = paricleInst.getData()
        self.assertIsNotNone(a)
        self.assertEqual(len(a['count']), len(a['date']))
        div = paricleInst.makePlot()
        self.assertIsNotNone(div)


unittest.main()
