import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import datetime

BatV = "BatV"
Bat_status = "Bat_status"
Ext_sensor = "Ext_sensor"
Hum_SHT = "Hum_SHT"
TempC_DS = "TempC_DS"
TempC_SHT = "TempC_SHT"
fileName = "20240301.txt"

def defineInputFileDirectory():
    # FIXME - Change the input file directory to the correct one
    global fileName
    # fileName = str(input("\nEnter the file name: "))
    inputFileDirectory = "C:\\Users\\Mateus\\Documents\\GitHub\\MQTT_TTN_Python\\" + fileName
    return inputFileDirectory

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

def collectDataFromPayload(dataCollect):
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

def createDataFrame(batV, batStatus, extSensor, humidity_SHT, tempC_DS, tempC_SHT):
    data = {
        "BatV": batV,
        "BatStatus": batStatus,
        "ExtSensor": extSensor,
        "Humidity_SHT": humidity_SHT,
        "TemperatureC_DS": tempC_DS,
        "TemperatureC_SHT": tempC_SHT
    }

    df = pd.DataFrame(data)
    return df

def start(): 
    inputFileDirectory = defineInputFileDirectory()
    decodedValue, readTime = readInputFile(inputFileDirectory)
    batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT = collectDataFromPayload(decodedValue)
    
    # DEBUG
    # print(f"\nBatV: {batV}")
    # print(f"BatStatus: {batStatus}")
    # print(f"ExtSensor: {extSensor}")
    # print(f"Humidity_SHT: {humidity_SHT}")
    # print(f"TemperatureC_DS: {temperatureC_DS}")
    # print(f"TemperatureC_SHT: {temperatureC_SHT}")
    # print(f"Time: {readTime}\n")
    
    formatedTime = []
    for i in range(len(readTime)):
        hour = datetime.datetime.strptime(readTime[i], "%Y-%m-%dT%H:%M:%S.%f")
        formatedHour = hour.strftime("%H:%M:%S")
        formatedTime.append(formatedHour)    

    df = createDataFrame(batV, batStatus, extSensor, humidity_SHT, temperatureC_DS, temperatureC_SHT)

    st.header(f"Data Frame from Payload: {fileName}")
    st.table(df)

    fig = plt.figure(figsize = (8,4))
    # plt.plot(df.index, df['BatV'], label = "BatV")
    # plt.plot(df.index, df['BatStatus'], label = "BatStatus")
    # plt.plot(df.index, df['ExtSensor'], label = "ExtSensor")
    # plt.plot(df.index, df['Humidity_SHT'], label = "Humidity_SHT")
    plt.plot(df.index, df['TemperatureC_DS'], label = "TemperatureC_DS")
    plt.plot(formatedTime, df['TemperatureC_SHT'], label = "TemperatureC_SHT")
    plt.xlabel("Horário da Leitura (HH:MM:SS)")
    plt.ylabel("Valores de Temperatura (°C)")
    plt.legend()
    st.pyplot(fig)
    
