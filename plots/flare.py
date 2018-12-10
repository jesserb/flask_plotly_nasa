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

class SolarFlares:

    def __init__(self):
        self.allData = {'x': [], 'y': [], 'class': [], 'info': []}


    def getData(self):
        # connect to database
        conn = sqlite.connect('./database/nasa.db')
        cur = conn.cursor()

        sql = '''
            SELECT S.Start, S.Type, T.XrayOutput, I.Name
            FROM SolarFlares AS S
            JOIN SolarFlareTypes As T ON T.Type=S.Type
            JOIN SolarFlareInstruments AS I ON I.SolarFlareID=S.ID
            ORDER BY S.Start
        '''
        data = cur.execute(sql).fetchall()
        for d in data:
            self.allData['x'].append(d[0].split('T')[0])
            self.allData['y'].append(m.log10(d[2])) 
            self.allData['class'].append(d[1][0]) 
            self.allData['info'].append(
                ('<b>Brightness:</b> {}<br><b>Class:</b> {}<br><b>Instrument:</b> {}').format((d[2]), d[1], d[3])
            )
        conn.close()
        return self.allData


    def getLayout(self):
        return go.Layout(
            title='<b>Solar Flares</b>',
            titlefont=dict(
                size=45,
                color='#707070'
            ),
            width= 1200,
            height= 680,
            xaxis=dict(
                title='YEAR',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=18
                ),
                tickangle=45,
                tickfont=dict(
                    family='Old Standard TT, serif',
                    size=18,
                    color='black'
                )
            ),
            yaxis= dict(
                side='right',
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False
            ),
            yaxis2=dict(
                overlaying='y',
                title='<b>X-Ray Brightness<br>(Watts/m^2)<br></b>',
                titlefont=dict(
                    size=20,
                ),
                ticktext=['0.01mu', '0.1mu','1mu','10mu','100mu', '1000mu'],
                tickvals=[m.log10(1e-8), m.log10(1e-7),m.log10(1e-6),m.log10(1e-5),m.log10(1e-4), m.log10(1e-3)],
                tickangle=-45,
                side='left'
            )
        )

    def makePlot(self):
        trace0 = go.Scatter(
            x = self.allData['x'],
            y = self.allData['y'],
            hoverinfo='none',
            showlegend = False,
            line = dict(
                color = ('#707070'),
                width = 2
            )
        )
        trace1 = go.Scatter(
            x = self.allData['x'],
            y = self.allData['y'],
            text = self.allData['info'],
            yaxis='y2',
            hoverinfo = 'text',
            mode='markers',
            showlegend = False,
            marker=dict(
                size=10,
                line = dict(width=1),
                color = self.allData['y'], #set color equal to a variable
                colorscale='Hot',
                showscale=True,
                colorbar = dict(
                    title = '<b>Class</b>',
                    titleside = 'top',
                    tickvals = [m.log10(1.5e-7),m.log10(1e-6),m.log10(1e-5),m.log10(0.0001)],
                    ticktext = ['<b>B</b>', '<b>C</b>', '<b>M</b>', '<b>X</b>'],
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
