
## Есть ли готовые библиотеки виджетов для web приложений


1. Dash DAQ
<br>Dash DAQ (Data Acquisition) - это библиотека для создания приборных панелей и визуализаций в Dash. Она включает в себя различные компоненты, такие как стрелочные приборы, термометры, переключатели и многое другое.

**_Пример использования стрелочного прибора (Gauge) в Dash DAQ:_**
```
import dash
import dash_daq as daq
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
    daq.Gauge(
        id='my-gauge',
        value=6,
        min=0,
        max=10,
        showCurrentValue=True,
        units="A",
        label='Amperemeter'
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
```


2. Plotly
<br>Plotly - это библиотека для создания интерактивных графиков и визуализаций. Она также поддерживает создание стрелочных приборов с помощью go.Indicator.

**_Пример использования стрелочного прибора в Plotly:_**
```
import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=270,
    title={'text': "Speed"},
    gauge={'axis': {'range': [None, 500]}}
))

fig.show()
```

3. D3.js
<br>D3.js - это мощная библиотека для создания динамических и интерактивных визуализаций данных с использованием HTML, SVG и CSS. Существует множество примеров и плагинов для создания стрелочных приборов.

**_Пример использования стрелочного прибора в D3.js:_**
```
<!DOCTYPE html>
<meta charset="utf-8">
<style>
  .gauge {
    width: 200px;
    height: 200px;
  }
</style>
<body>
<div id="gauge"></div>
<script src="https://d3js.org/d3.v5.min.js"></script>
<script src="https://rawgit.com/tomerdmnt/d3-gauge/master/dist/d3-gauge.min.js"></script>
<script>
  var gauge = d3.gauge()
    .min(0)
    .max(100)
    .value(50)
    .label("Voltage")
    .width(200)
    .height(200);

  d3.select("#gauge").call(gauge);
</script>
</body>
</html>
```

4. JustGage
<br>JustGage - это библиотека для создания интерактивных стрелочных приборов на основе SVG. Она проста в использовании и поддерживает множество настроек.

**_Пример использования JustGage:_**
```
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/justgage"></script>
  <script src="https://cdn.jsdelivr.net/npm/raphael"></script>
</head>
<body>
  <div id="gauge" style="width:200px; height:160px;"></div>
  <script>
    var g = new JustGage({
      id: "gauge",
      value: 72,
      min: 0,
      max: 100,
      title: "Temperature"
    });
  </script>
</body>
</html>
```

#### Эти библиотеки предоставляют широкий спектр возможностей для создания динамических и интерактивных стрелочных приборов