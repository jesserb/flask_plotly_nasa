import sqlite3 as sqlite
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from matplotlib import rc, font_manager
import matplotlib.pyplot as plt
import numpy as np
from plots.plotly_secrets import *
import math as m
plotly.tools.set_credentials_file(username=P_USERNAME, api_key=P_API_KEY)

class CME:

    def __init__(self):
        self.allData = {'long': [], 'lat': [], 'speed': [], 'info': []}
        self.markerSize = []


    def getData(self):
        # connect to database
        conn = sqlite.connect('./database/nasa.db')
        cur = conn.cursor()

        sql = '''
            SELECT C.Longitude, C.Latitude, C.Speed, C.Note, C.Type, C.Time, F.Type
            FROM CME AS C
            JOIN SolarFlares As F ON F.LinkedEventID=C.CMEID
        '''
        data = cur.execute(sql).fetchall()
        for d in data:
            self.allData['long'].append(d[0])
            self.allData['lat'].append(d[1])
            self.allData['speed'].append(d[2]) 
            self.allData['info'].append(
                ('''
                    <b>TYPE:</b> {}<br>
                    <b>SOLAR FLARE TYPE:</b> {}<br>
                    <b>DATE/TIME:</b> {}<br>
                    <b>SPEED:</b> {}<br>
                    <b>NOTE:</b> {}<br>
                ''').format(d[4], d[6], d[5], d[2], d[3])
            )
            self.markerSize.append(d[2]/60)
        conn.close()
        return self.allData
    
    def getLayout(self):
        return go.Layout(
            title='<b>Coronal Mass Ejections</b>',
            titlefont=dict(
                size=45,
                color='#707070'
            ),
            width= 900,
            height= 900,
            xaxis=dict(
                title='Longitude',
                range=[-200,200],
                showgrid=False,
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=18
                ),
            ),
            yaxis= dict(
                title='Latitude',
                range=[-200,200],
                showgrid=False,
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=18
                ),
            )
        )

    def makePlot(self):
        trace0 = go.Scatter(
            x = [0],
            y = [0],
            showlegend = False,
            mode='markers',
            hoverinfo='none',
            marker=dict(
                size=650,
                line = dict(width=1),
                color = '#a82406', #set color equal to a variable
            )
        )
        trace1 = go.Scatter(
            x = self.allData['long'],
            y = self.allData['lat'],
            text = self.allData['info'],
            hoverinfo = 'text',
            showlegend = False,
            mode='markers',
            marker=dict(
                size=self.markerSize,
                line = dict(width=1),
                color = self.allData['speed'],
                colorscale='Viridis',
                colorbar = dict(
                    title = '<b>Velocity</b>',
                    titleside = 'top',
                    ticks = 'outside'
                )
            )
        )

        return [trace0, trace1]


    def plot(self):
        data = self.makePlot()
        layout = self.getLayout()
        fig = go.Figure(data=data, layout=layout)
        div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
        return div

