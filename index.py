# A script to pull out associatedCount values from DNA Spaces' firehose stream, for an occupancy display - based on Simon Light's COVID-Entry-Exit-system
# (see https://github.com/SimonLight001/COVID-Entry-Exit-system)

import jwt
import requests
import json
import socket
import time
import os
from datetime import datetime


def get_API_Key_and_auth():
    # Gets public key from spaces and places in correct format
    print("-- No API Key Found --")
    pubKey = requests.get(
        'https://partners.dnaspaces.io/client/v1/partner/partnerPublicKey/')
    pubKey = json.loads(pubKey.text)
    pubKey = pubKey['data'][0]['publicKey']
    pubKey = '-----BEGIN PUBLIC KEY-----\n' + pubKey + '\n-----END PUBLIC KEY-----'

    # Gets user to paste in generated token from app
    token = input('Enter token here: ')

    # Decodes JSON Web Token to get JSON out
    decodedJWT = jwt.decode(token, pubKey)
    decodedJWT = json.dumps(decodedJWT, indent=2)
    # print(decodedJWT)

    # picks up required values out of JWT
    decodedJWTJSON = json.loads(decodedJWT)
    appId = decodedJWTJSON['appId']
    activationRefId = decodedJWTJSON['activationRefId']

    # creates payloads and headers ready to activate app
    authKey = 'Bearer ' + token
    payload = {'appId': appId, 'activationRefId': activationRefId}
    header = {'Content-Type': 'application/json', 'Authorization': authKey}

    # Sends request to spaces with all info about JWT to confirm its correct, if it is, the app will show as activated
    activation = requests.post(
        'https://partners.dnaspaces.io/client/v1/partner/activateOnPremiseApp/', headers=header, json=payload)

    print(activation.text)
    activation = json.loads(activation.text)
    print(activation['message'])

    apiKey = activation['data']['apiKey']
    f = open("API_KEY.txt", "a")
    f.write(apiKey)
    f.close()
    return apiKey


# work around to get IP address on hosts with non resolvable hostnames
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP_ADRRESS = s.getsockname()[0]
s.close()
url = 'http://' + str(IP_ADRRESS) + '/'

try:
    if os.stat("API_KEY.txt").st_size > 0:
        f = open("API_KEY.txt")
        apiKey = f.read()
        f.close()
        print("-- API Key Found -- ")
        print("-- If you wanted to renew your API key, just delete the file API_KEY.txt --")
    else:
        apiKey = get_API_Key_and_auth()
except:
    apiKey = get_API_Key_and_auth()

s = requests.Session()
s.headers = {'X-API-Key': apiKey}
r = s.get(
    'https://partners.dnaspaces.io/api/partners/v1/firehose/events', stream=True)

# pull out associatedCount values based on location, write to a log file with a timestamp, then write to a temp txt file to be read from by rcvr.py
# this could probably be done in a more clever manner; feel free to improve!

for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        event = json.loads(decoded_line)
        eventType = event['eventType']
        if eventType == "DEVICE_COUNT":
            location = event['deviceCounts']['location']['name']
            if location == "<LOCATION_NAME_1>":
                assocCount = event['deviceCounts']['associatedCount']
                dt = str(datetime.now())
                with open('/var/www/YOURHOST.YOURDOMAIN.EDU/cbot/<LOCATION_NAME_1>.log',mode='a+') as f:
                    f.write(dt+' '+location+' associated count = '+str(assocCount)+'\n')
                with open('/var/www/YOURHOST.YOURDOMAIN.EDU/cbot/<LOCATION_NAME_1>.txt',mode='w') as g:
                    g.write(str(assocCount))
            elif location == "<LOCATION_NAME_2>":
                assocCount = event['deviceCounts']['associatedCount']
                dt = str(datetime.now())
                with open('/var/www/YOURHOST.YOURDOMAIN.EDU/cbot/<LOCATION_NAME_2>.log',mode='a+') as f:
                    f.write(dt+' '+location+' associated count = '+str(assocCount)+'\n')
                with open('/var/www/YOURHOST.YOURDOMAIN.EDU/cbot/<LOCATION_NAME_2>.txt',mode='w') as g:
                    g.write(str(assocCount))
			# add additional locations to this loop as required
			