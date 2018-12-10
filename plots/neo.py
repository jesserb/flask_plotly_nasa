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

class NEO:

    def __init__(self):
        self.hazard = {'size': [], 'dist': [], 'color': '', 'markerSize': [], 'info': []}
        self.nonHazard = {'size': [], 'dist': [], 'color': '', 'markerSize': [], 'info': []}

    def getData(self):
        # connect to database
        conn = sqlite.connect('./database/nasa.db')
        cur = conn.cursor()

        sql = '''
            SELECT Diameter, ClosestApproach, Hazardous, Name
            FROM NearEarthObjects
        '''
        data = cur.execute(sql).fetchall()
        for d in data:
            if d[2]:
                self.hazard['size'].append(d[0])
                self.hazard['dist'].append(d[1])
                self.hazard['color'] = '#9F1C00'
                self.hazard['markerSize'].append(d[0]*50)
                self.hazard['info'].append(
                    ('''
                        <b>NAME:</b> {}<br>
                        <b>SIZE:</b> {}km<br>
                        <b>CLOSEST APPROACH:</b> {}km<br>
                        <b>HAZARDOUS:</b> True<br>
                    ''').format(d[3], d[0], d[1])
                )
            else:
                self.nonHazard['size'].append(d[0])
                self.nonHazard['dist'].append(d[1])
                self.nonHazard['color'] = '#006F9F'
                self.nonHazard['markerSize'].append(d[0]*50)
                self.nonHazard['info'].append(
                    ('''
                        <b>NAME:</b> {}<br>
                        <b>SIZE:</b> {}km<br>
                        <b>CLOSEST APPROACH:</b> {}km<br>
                        <b>HAZARDOUS:</b> False<br>
                    ''').format(d[3], d[0], d[1])
                )
        conn.close()
        return self.hazard, self.nonHazard
    
    def getLayout(self):
        return go.Layout(
            title='<b>Near Earth Objects (NEO)</b>',
            titlefont=dict(
                size=45,
                color='#707070'
            ),
            width= 1100,
            height= 700,
            xaxis=dict(
                title='<b>Closest Approach</b> (km)',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=25
                ),
                tickfont=dict(
                    family='Old Standard TT, serif',
                    size=18,
                    color='black'
                )
            ),
            yaxis= dict(
                title='<b>Diameter</b> (km)',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=25
                ),
                tickfont=dict(
                    family='Old Standard TT, serif',
                    size=18,
                    color='black'
                )
            ),
            legend=dict(
                x=.8,
                y=.9,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=16,
                    color='#000'
                )
            )
        )

    def makePlot(self):
        trace0 = go.Scatter(
            x = self.hazard['dist'],
            y = self.hazard['size'],
            text = self.hazard['info'],
            name='Potentially Hazardous',
            hoverinfo = 'text',
            mode='markers',
            marker=dict(
                size = self.hazard['markerSize'],
                line = dict(width=1),
                color = self.hazard['color']
            )
        )
        trace1 = go.Scatter(
            x = self.nonHazard['dist'],
            y = self.nonHazard['size'],
            text = self.nonHazard['info'],
            name='Not Hazardous',
            hoverinfo = 'text',
            mode='markers',
            marker=dict(
                size = self.nonHazard['markerSize'],
                line = dict(width=1),
                color = self.nonHazard['color']
            )
        )


        data = [trace0, trace1]
        layout = self.getLayout()
        fig = go.Figure(data=data, layout=layout)
        div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
        return div
