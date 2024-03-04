import datetime
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc

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
    # FIXME - Change the input file directory to the correct one
    global inputFileName
    # inputFileName = str(input("\nEnter the input file name: "))
    file = inputFileDirectory + inputFileName
    return file

def readInputFile(inputFileDirectory):
    decodedValue = []
    time = []
    start = []
    end = []
    
    with open(inputFileDirectory, 'r') as file:
        data = file.read().replace('\n', '')

        for i in range(len(data)):
            if data[i] == "2" and data[i+1] == "0" and data[i+2] == "2" and data[i+3] == "4" and data[i+29] == "Z":
                time.append(data[i:i+23])
            if data[i] == "{":
                start.append(i)
            if data[i] == "}":
                end.append(i)

        for i in range(len(start)):
            decodedValue.append(data[start[i]+1:end[i]])
    
    return decodedValue, time

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

    # DEBUG
    # print()
    for i in range(len(dataCollect)):
        # print(f"Each Data Collect: {dataCollect[i]}")
        
        for j in range(len(dataCollect[i])):
            dataCollect[i][j] = dataCollect[i][j].replace(" ", "").split(':')

            if dataCollect[i][j][0] == BatV:
                batVList.append(dataCollect[i][j][1])
            # Get BatStatus for each data collect

            if dataCollect[i][j][0] == Bat_status:
                batStatusList.append(dataCollect[i][j][1])
            # Get ExtSensor for each data collect

            if dataCollect[i][j][0] == Ext_sensor:
                extSensorList.append(dataCollect[i][j][1])
            # Get HumiditySHT for each data collect

            if dataCollect[i][j][0] == Hum_SHT:
                humidity_SHTList.append(dataCollect[i][j][1])
            # Get TemperatureDS for each data collect

            if dataCollect[i][j][0] == TempC_DS:
                temperatureC_DSList.append(dataCollect[i][j][1])
            # Get TemperatureSHT for each data collect
            
            if dataCollect[i][j][0] == TempC_SHT:
                temperatureC_SHTList.append(dataCollect[i][j][1])
            
    return batVList, batStatusList, extSensorList, humidity_SHTList, temperatureC_DSList, temperatureC_SHTList

def formatTime(time):
    formatedTime = []
    for i in range(len(time)):
        extractedDate = datetime.datetime.strptime(time[i], "%Y-%m-%dT%H:%M:%S.%f")
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

    df = pd.DataFrame(data)
    return df

def writeCsvFile(df):
    df.to_csv(outputDirectory + outputFileName, index = True)

def plotGraph(df):
    global app
    df = pd.read_csv(outputDirectory + outputFileName)
    temperatureFig = createFigure(df, ['TemperatureC_DS', 'TemperatureC_SHT'], "Temperature", " (°C)")
    humidityFig = createFigure(df, ['Humidity_SHT'], "Humidity", " (%)")

    app.layout = html.Div([
        dcc.Graph(figure=temperatureFig, id='temperature-graph', style={'height': '100vh'}),
        dcc.Graph(figure=humidityFig, id='humidity-graph', style={'height': '100vh'})
    ])

    app.run_server(debug=True)

def createFigure(df, columns, title, unit):
    temperatureFig = px.line(
        df,
        title = title + " Data from '" + inputFileName + "' file.",
        x='DateTime', y=columns,
        range_x=[datetime.datetime.strptime(df['DateTime'][0], "%H:%M:%S"), datetime.datetime.strptime(df['DateTime'][len(df)-1], "%H:%M:%S")],
        labels={'DateTime': 'Time (HH:MM:SS)', 'value': title + unit},
        markers=True,
        template="seaborn"
    )
    return temperatureFig

def start():
    inputFileDirectory = defineInputFileDirectory()
    decodedValue, readTime = readInputFile(inputFileDirectory)
    time = formatTime(readTime)
    batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT = extractPayloadData(decodedValue)

    df = createDataFrame(time, batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT)
    writeCsvFile(df)
    plotGraph(df)

def main():
    start()
