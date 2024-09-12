#!/usr/bin/env python3

from dash import Dash, html, dcc, callback, Output, Input
import dash_daq as daq
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests

# Параметры подключения к QuestDB
host = 'http://gitlab.ivl.ua:9000'
sql_query = """
SELECT DHT_Temperature, DHT_Humidity,
BME_Temperature, BME_Humidity, BME_Pressure,
DS_Temperature1, DS_Temperature2, timestamp
FROM sensors
ORDER BY timestamp DESC
LIMIT 60;
"""

# Функция для получения данных из QuestDB
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

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Weather Sensor Data', style={'textAlign': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # обновление каждые 5 секунд
        n_intervals=0
    ),

        html.Div([
        dcc.Graph(id='temperature-graph'),
        html.Div([
            daq.Thermometer(
                id='thermometer-dht',
                label='DHT Temperature',
                min=-10,
                max=50,
                value=0,
                showCurrentValue=True,
                units='°C'
            ),
            daq.Thermometer(
                id='thermometer-bme',
                label='BME Temperature',
                min=-10,
                max=50,
                value=0,
                showCurrentValue=True,
                units='°C'
            ),
            daq.Thermometer(
                id='thermometer-ds1',
                label='DS Temperature 1',
                min=-10,
                max=50,
                value=0,
                showCurrentValue=True,
                units='°C'
            ),
            daq.Thermometer(
                id='thermometer-ds2',
                label='DS Temperature 2',
                min=-10,
                max=50,
                value=0,
                showCurrentValue=True,
                units='°C'
            )
        ], style={'display': 'flex', 'justify-content': 'space-around'})
       
    ]),


    dcc.Graph(id='humidity-graph'),
    dcc.Graph(id='pressure-graph')
], style={'width': '50%', 'margin': 'auto'})  # Уменьшение ширины контейнера до 50%

@app.callback(
    Output('temperature-graph', 'figure'),
    Output('humidity-graph', 'figure'),
    Output('pressure-graph', 'figure'),
    Output('thermometer-dht', 'value'),
    Output('thermometer-bme', 'value'),
    Output('thermometer-ds1', 'value'),
    Output('thermometer-ds2', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    data = get_data()
    if data:
        df = pd.DataFrame(data, columns=[
            'DHT_Temperature', 'DHT_Humidity',
            'BME_Temperature', 'BME_Humidity', 'BME_Pressure',
            'DS_Temperature1', 'DS_Temperature2', 'timestamp'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # График температуры
        fig_temp = px.line(df, x='timestamp', y=['DHT_Temperature', 'BME_Temperature', 'DS_Temperature1', 'DS_Temperature2'])
        fig_temp.update_layout(
            yaxis_title='Temperature (°C)',
            xaxis_title=None,
            height=200,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        # График влажности
        fig_humidity = px.line(df, x='timestamp', y=['DHT_Humidity', 'BME_Humidity'])
        fig_humidity.update_layout(
            yaxis_title='Humidity (%)',
            xaxis_title=None,
            height=200,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        # График давления
        fig_pressure = px.line(df, x='timestamp', y='BME_Pressure')
        fig_pressure.update_layout(
            yaxis_title='Pressure (mm Hg)',
            xaxis_title=None,
            height=200,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        '''
        # Создание термометров с помощью Plotly
        def create_thermometer(value, title):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': title},
                gauge={'axis': {'range': [-10, 50]}}
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            return fig
        '''

        # Значения для термометров
        dht_temp = df['DHT_Temperature'].iloc[-1]
        bme_temp = df['BME_Temperature'].iloc[-1]
        ds_temp1 = df['DS_Temperature1'].iloc[-1]
        ds_temp2 = df['DS_Temperature2'].iloc[-1]

        '''
        fig_thermometer_dht = create_thermometer(dht_temp, 'DHT Temperature')
        fig_thermometer_bme = create_thermometer(bme_temp, 'BME Temperature')
        fig_thermometer_ds1 = create_thermometer(ds_temp1, 'DS Temperature 1')
        fig_thermometer_ds2 = create_thermometer(ds_temp2, 'DS Temperature 2')
        '''
        return fig_temp, fig_humidity, fig_pressure, dht_temp, bme_temp, ds_temp1, ds_temp2
    return {}, {}, {}, 0, 0, 0, 0

if __name__ == '__main__':
    app.run(debug=True)
