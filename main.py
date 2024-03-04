import datetime
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
from dash.exceptions import PreventUpdate

BatV = "BatV"
Bat_status = "Bat_status"
Ext_sensor = "Ext_sensor"
Hum_SHT = "Hum_SHT"
TempC_DS = "TempC_DS"
TempC_SHT = "TempC_SHT"
inputFileName = "20240301.txt"
outputFileName = "output.csv"
inputFileDirectory = "C:\\Users\\Mateus\\Documents\\GitHub\\MQTT_TTN_Python\\"
outputDirectory = "C:\\Users\\Mateus\\Documents\\GitHub\\Dashboard_Python\\output\\"

app = Dash(__name__)

def defineInputFileDirectory():
    global inputFileName
    file = inputFileDirectory + inputFileName
    return file

def readInputFile(inputFileDirectory):
    decodedValue = []
    rawDateTime = []
    start = []
    end = []
    
    with open(inputFileDirectory, 'r') as file:
        data = file.read().replace('\n', '')

        for i in range(len(data)):
            if data[i] == "2" and data[i+1] == "0" and data[i+2] == "2" and data[i+3] == "4" and data[i+29] == "Z":
                rawDateTime.append(data[i:i+23])
            if data[i] == "{":
                start.append(i)
            if data[i] == "}":
                end.append(i)

        for i in range(len(start)):
            decodedValue.append(data[start[i]+1:end[i]])
    
    return decodedValue, rawDateTime

def extractPayloadData(dataCollect):
    separator = ","
    batVList = []
    batStatusList = []
    extSensorList = []
    humidity_SHTList = []
    temperatureC_DSList = []
    temperatureC_SHTList = []

    [i.split(separator) for i in dataCollect]
    dataCollect = list(map(lambda x: x.replace("'", ""), dataCollect))
    dataCollect = list(map(lambda x: x.split(separator), dataCollect))

    for i in range(len(dataCollect)):        
        for j in range(len(dataCollect[i])):
            dataCollect[i][j] = dataCollect[i][j].replace(" ", "").split(':')

            if dataCollect[i][j][0] == BatV:
                batVList.append(dataCollect[i][j][1])

            if dataCollect[i][j][0] == Bat_status:
                batStatusList.append(dataCollect[i][j][1])

            if dataCollect[i][j][0] == Ext_sensor:
                extSensorList.append(dataCollect[i][j][1])

            if dataCollect[i][j][0] == Hum_SHT:
                humidity_SHTList.append(dataCollect[i][j][1])

            if dataCollect[i][j][0] == TempC_DS:
                temperatureC_DSList.append(dataCollect[i][j][1])

            if dataCollect[i][j][0] == TempC_SHT:
                temperatureC_SHTList.append(dataCollect[i][j][1])
            
    return batVList, batStatusList, extSensorList, humidity_SHTList, temperatureC_DSList, temperatureC_SHTList

def formatTime(rawDateTime):
    formatedTime = []
    for i in range(len(rawDateTime)):
        extractedDate = datetime.datetime.strptime(rawDateTime[i], "%Y-%m-%dT%H:%M:%S.%f")
        formatedTime.append(extractedDate.strftime("%H:%M:%S"))    
    return formatedTime

def createDataFrame(formatedTime, batV, batStatus, extSensor, humidity_SHT, tempC_DS, tempC_SHT):
    data = {
        "DateTime": formatedTime,
        "BatV": batV,
        "BatStatus": batStatus,
        "ExtSensor": extSensor,
        "Humidity_SHT": humidity_SHT,
        "TemperatureC_DS": tempC_DS,
        "TemperatureC_SHT": tempC_SHT
    }
    return pd.DataFrame(data)

def writeCsvFile(dataFrame):
    dataFrame.to_csv(outputDirectory + outputFileName, index = True)

def createFigure(dataFrame, columns, title, unit):
    temperatureFig = px.line(
        dataFrame,
        title = title + " Data from '" + inputFileName + "' file.",
        x='DateTime', y=columns,
        labels={'DateTime': 'Time (HH:MM:SS)', 'value': title + unit},
        markers=True,
        template="seaborn"
    )
    return temperatureFig

# Callback to update the graph every X seconds
@app.callback(
    [Output('temperature-graph', 'figure'),
     Output('humidity-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]   
)
def update_graph(n_intervals):
    try:
        inputFileDirectory = defineInputFileDirectory()
        decodedValue, readTime = readInputFile(inputFileDirectory)
        formattedDateTime = formatTime(readTime)
        batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT = extractPayloadData(decodedValue)

        dataFrame = createDataFrame(formattedDateTime, batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT)
        writeCsvFile(dataFrame)

        temperatureFig = createFigure(dataFrame, ['TemperatureC_DS'], "Temperature", " (°C)")
        humidityFig = createFigure(dataFrame, ['Humidity_SHT'], "Humidity", " (%)")

        return temperatureFig, humidityFig

    except PreventUpdate:
        raise PreventUpdate

def setup():
    app.layout = html.Div([
        dcc.Interval(
            id='interval-component',
            interval=3000,  # in milliseconds
            n_intervals=0
        ),
        dcc.Graph(id='temperature-graph', style={'height': '100vh'}),
        dcc.Graph(id='humidity-graph', style={'height': '100vh'})
    ])

def main():
    setup()
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
