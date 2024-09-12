import sys
import subprocess
import flask
from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .models import User, db

import matplotlib.pyplot as plt
import io
import requests


bp = Blueprint('main', __name__)


@bp.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')

### ======================================================================

# Новый код для получения данных и отображения графиков
host = 'http://gitlab.ivl.ua:9000'

sql_query = """SELECT DHT_Temperature, DHT_Humidity,
                    BME_Temperature, BME_Humidity, BME_Pressure,
                    DS_Temperature1, DS_Temperature2, timestamp
            FROM sensors
            ORDER BY timestamp DESC
            LIMIT 60;
            """

def get_data():
    try:
        response = requests.get(
            host + '/exec',
            params={'query': sql_query}
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json['dataset']
    except Exception as e:
        print("Error fetching data:", e)
        return None

def create_figure(data):
    if data is None:
        print("No data available to create figure.")
        return None
        
    timestamps = [row[7] for row in data]
    dht_temp = [row[0] for row in data]
    dht_hum = [row[1] for row in data]
    bme_temp = [row[2] for row in data]
    bme_hum = [row[3] for row in data]
    bme_press = [row[4] for row in data]
    ds_temp1 = [row[5] for row in data]
    ds_temp2 = [row[6] for row in data]

    window_size = 10
    bme_temp_sum = sum(bme_temp[:window_size])
    bme_temp_avg = [bme_temp_sum / window_size]
    for i in range(window_size, len(bme_temp)):
        bme_temp_sum = bme_temp_sum - bme_temp[i - window_size] + bme_temp[i]
        bme_temp_avg.append(bme_temp_sum / window_size)

    #fig, ax = plt.subplots(4, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [1.2, 1.2, 1.2, 1.2]})

    fig, ax = plt.subplots(4, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [1, 1, 1, 1]})
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, hspace=0.2)

    ax[0].plot(timestamps[window_size-1:], bme_temp_avg, label='BME280 Temperature (Moving Average)')
    ax[0].set_ylabel('Temperature (°C)')
    ax[0].legend()
    ax[1].plot(timestamps, dht_temp, label='DHT Temper')
    ax[1].plot(timestamps, bme_temp, label='BME Temper')
    ax[1].plot(timestamps, ds_temp1, label='DS Temper 1')
    ax[1].plot(timestamps, ds_temp2, label='DS Temper 2')
    ax[1].plot(timestamps, ds_temp2, label='DS Temper 3')
    ax[1].set_ylabel('Temperature (°C)')
    ax[1].legend()
    ax[2].plot(timestamps, dht_hum, label='DHT Humidity')
    ax[2].plot(timestamps, bme_hum, label='BME Humidity')
    ax[2].set_ylabel('Humidity (%)')
    ax[2].legend()
    ax[3].plot(timestamps, bme_press, label='BME Pressure')
    ax[3].set_ylabel('Pressure (mm hg bar)')
    ax[3].legend()
    for a in ax:
        a.set_xlabel('Timestamp')
        a.legend()
        a.grid(True)
        xticks = a.get_xticks()
        a.set_xticks(xticks[::4])
        a.set_xticklabels([timestamps[int(i)] for i in xticks[::4]])
    fig.autofmt_xdate()
    return fig

### ------------------------------------------------------------------------

'''
        data = {
            'region': 'Region1',
            'post': randint(1, 10),
            'bme': {
                't': val,
                'h': val,
                'p': val
            },
            'ds': {
                't1': val,
                't2': val,
                't3': val
            },
            'dht': {
                't': val,
                'h': val
            },
            'timestamp': r.now()
        }
'''

def get_terminal_output():
    data = get_data()
            
    output = []
    header = "{:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<30}".format(
        "ROW_num", "DHT_T", "DHT_H", "BME_T", "BME_H", "BME_P", "DS_T1", "DS_T2", "DS_T3", "Timestamp"
    )
    separator = "-------- " * 9 + "------------------------------"
    output.append(separator)
    output.append(f"total_rows {len(data)}")

    output.append(separator)
    for i, row in enumerate(data):
        output.append("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<30}".format(
            i,

            row[0],
            row[1],

            row[2],
            row[3],
            row[4],

            row[5],
            row[6],
            row[7],

            row[8]
        ))
    output.append(separator)
    output.append(header)
    output.append(separator)
    return "\n".join(output)

### -----------------------------------------------------------------------

@bp.route('/plot.png')
def plot_png():
    data = get_data()
    fig = create_figure(data)
    output = io.BytesIO()
    fig.savefig(output, format='png')
    output.seek(0)
    return send_file(output, mimetype='image/png')

@bp.route('/terminal_output')
def terminal_output():
    return get_terminal_output()

@bp.route('/rethinkdb')
def rethinkdb():
    terminal_output = get_terminal_output()
    return render_template('rethinkdb.html', title='Working with rethinkdb', terminal_output=terminal_output)

### ======================================================================
