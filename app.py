from flask import Flask, render_template
import sqlite3 as sqlite
from plots.flare import *
from plots.cme import *
from plots.neo import *
from plots.particle import *
from plots.plotly_secrets import *


app = Flask(__name__)


@app.route('/')
def homepage():

    # connect to database
    conn = sqlite.connect('./database/nasa.db')
    cur = conn.cursor()

    # query daabase for information on eaxch section
    cmeInfo   = cur.execute('SELECT Text FROM WikiScrapes WHERE ID="cme"').fetchall()[0][0]
    flareInfo = cur.execute('SELECT Text FROM WikiScrapes WHERE ID="flare"').fetchall()[0][0]
    particleInfo   = cur.execute('SELECT Text FROM WikiScrapes WHERE ID="particle"').fetchall()[0][0]
    neoInfo   = cur.execute('SELECT Text FROM WikiScrapes WHERE ID="neo"').fetchall()[0][0]
    conn.close()
    return render_template('nasa.html', CME_INFO=cmeInfo, FLARE_INFO=flareInfo, PARTICLE_INFO=particleInfo, NEO_INFO=neoInfo)


@app.route('/solarflare', methods=['POST', 'GET'])
def flare(): 
    plot = SolarFlares()
    plot.getData()
    div = plot.plot()

    return render_template('plot.html', GRAPH=div)


@app.route('/cme', methods=['POST', 'GET'])
def cme(): 
    plot = CME()
    plot.getData()
    div = plot.plot()

    return render_template('plot.html', GRAPH=div)


@app.route('/neo', methods=['POST', 'GET'])
def neo(): 
    plot = NEO()
    plot.getData()
    div = plot.makePlot()

    return render_template('plot.html', GRAPH=div)

@app.route('/sese', methods=['POST', 'GET'])
def sese(): 
    plot = SESE()
    plot.getData()
    div = plot.makePlot()

    return render_template('plot.html', GRAPH=div)


if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(host='0.0.0.0', debug=True)
