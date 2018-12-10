import sqlite3 as sqlite
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from matplotlib import rc, font_manager
import matplotlib.pyplot as plt
import numpy as np
from plots.plotly_secrets import *
import math as m
from plots.flare import *
from plots.cme import *
plotly.tools.set_credentials_file(username=P_USERNAME, api_key=P_API_KEY)

class SESE:

    def __init__(self):
        self.allData = {'count': [], 'date': []}


    def getData(self):
        # connect to database
        conn = sqlite.connect('./database/nasa.db')
        cur = conn.cursor()

        sql = '''
            SELECT P.Date, COUNT(*)
            FROM SolarEnergeticParticles AS P
            GROUP BY P.Date
        '''
        data = cur.execute(sql).fetchall()
        for d in data:
            self.allData['date'].append(d[0])
            self.allData['count'].append(d[1]) 
        conn.close()
        return self.allData

    def getLayout(self):
        return go.Layout(
            title='<b>Solar Energetic Particles (SEPE)</b>',
            titlefont=dict(
                size=45,
                color='#707070'
            ),
            width= 800,
            height= 500,
            xaxis=dict(
                title='<b>Number of SESE events</b>',
                domain=[0.03, 0.98],
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=25
                ),
                tickvals=[0, 5, 10, 15, 20, 25, 30, 35, 40],
                tickfont=dict(
                    family='Old Standard TT, serif',
                    size=18,
                    color='black'
                )
            ),
            yaxis= dict(
                title='<b>Year</b>',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=25
                ),
                position=0.00001,
                tickangle=-20,
                tickfont=dict(
                    family='Old Standard TT, serif',
                    size=18,
                    color='black'
                )
            )
        )


    def makePlot(self):
        data = [
            go.Bar(
                x=self.allData['count'],
                y=self.allData['date'],
                orientation = 'h',
                marker=dict(
                    color='#000'
                )
            )
        ]
        layout = self.getLayout()
        annotations = []
        for count, date in zip(self.allData['count'], self.allData['date']):
            if count > 8:
                annotations.append(
                    dict(
                        xref='x', yref='y',
                        x=(count/2), y=date, 
                        text=str(count) + ' events',
                        font=dict(
                            family='Arial', size=15,
                            color='#59F5FF'
                        ),
                        showarrow=False
                    )
                )
            else:
                annotations.append(
                    dict(
                        xref='x', yref='y',
                        x=(count+3), y=date, 
                        text='<b>' + str(count) + ' events</b>',
                        font=dict(
                            family='Arial', size=15,
                            color='#000'
                        ),
                        showarrow=False
                    )
                )
        layout['annotations'] = annotations
        fig = go.Figure(data=data, layout=layout)
        div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
        return div

