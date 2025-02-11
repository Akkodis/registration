from __future__ import print_function

import json
import time

import sqlalchemy as db
import requests

from threading import Thread

send = False
dataflowId = -1
topic = ""

engine = db.create_engine('mysql+pymysql://root:example@127.0.0.1:3306/5GMETA', isolation_level="READ UNCOMMITTED")
connection = engine.connect()
metadata = db.MetaData()
dataflows = db.Table('dataflows', metadata, autoload=True, autoload_with=engine)

def increase_interested_parties_counter(dataflowId):
    query = db.select([dataflows.columns.counter]).where(dataflows.columns.dataflowId == dataflowId)
    c = connection.execute(query).fetchone()["counter"] + 1

    query = db.update(dataflows).values({"counter": c}).where(dataflows.columns.dataflowId == dataflowId)
    connection.execute(query)

def decrease_interested_parties_counter(dataflowId):
    query = db.select([dataflows.columns.counter]).where(dataflows.columns.dataflowId == dataflowId)
    c = connection.execute(query).fetchone()["counter"] - 1

    query = db.update(dataflows).values({"counter": c}).where(dataflows.columns.dataflowId == dataflowId)
    connection.execute(query)


def sendKeepAlive():
    global send
    cnt = 0
    while(cnt < 2):
        cnt += 1
        time.sleep(5)
        r = requests.put("http://"+platformaddress+':12346/dataflows/'+str(dataflowId), json = (dataflowmetadata))
        print("Keepalive sent: ")
        print(r.text)
        send = r.json()['send']

platformaddress = "127.0.0.1"
registrationapi_port = "12346"

dataflowmetadata = {
    "dataTypeInfo": {
        "dataType": "cits",
        "dataSubType": "denm"
    },
    "dataInfo": {
        "dataFormat": "asn1_jer",
        "dataSampleRate": 0.0,
        "dataflowDirection": "upload",
        "extraAttributes": None,
    },
    "licenseInfo": {
        "licenseGeolimit": "europe",
        "licenseType": "profit"
    },
    "dataSourceInfo": {
        "timeZone": 10,
        "timeStratumLevel": 3,
        "sourceId": 1,
        "sourceType": "vehicle",
        "sourceLocationInfo": {
            "locationQuadkey": str(120223010111021111),
            "locationCountry": "ITA",
        }
    }   
}

if __name__ == "__main__":

    # Url to add a dataflow
    url = "http://"+platformaddress+':'+registrationapi_port+'/dataflows'

    # Send the JSON of the dataflow's metadata, and receive the dataflowId and the topic where to publish the messages
    r = requests.post(url, json = dataflowmetadata)
    if(r.status_code == 200):
        print("Registration sent.")
        print(r.text)
        r = r.json()
        dataflowId = r['id']
        topic = r['topic']
        send = r['send']
    else:
        print("Registration failed.")
        print(r.text)
        exit()

    #Start sending keepalives
    thread = Thread(target = sendKeepAlive)
    thread.start()

    # Start publishing messages in the received topic
    cnt = 0
    while(cnt < 10):
        #If need to send, send message every second
        if(send):
            print("Message sent.")
            if(cnt < 5):
                print("Failed.")
                exit(1)
        else:
            print("Message not sent.")
            if(cnt > 6):
                print("Failed.")
                exit(1)
        if(cnt == 0):
            increase_interested_parties_counter(dataflowId)
        time.sleep(int(1))
        cnt += 1
    
    exit(0)
