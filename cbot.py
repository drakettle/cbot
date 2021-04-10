# COVID Building Occupancy Thing - a simple wifi occupancy display for Cisco DNA Spaces firehose events
# last change: moved location dictionary to an external file
# last changed on: 2020-11-09
# devin.kettle@ubc.ca

from flask import Flask, request, render_template
import os
import json
from datetime import datetime
import ast
from pprint import pprint

# location_dict.txt stores these variables:
# maxcap: location occupancy limit
# dispname: text displayed at locn in the display_x.html templates
# offset: median value of o_raw location counts between 0100 & 0359 daily, to account for IoT / client count noise

with open('/var/www/YOURHOST.YOURDOMAIN.EDU/location_dict.txt', mode='r') as f:
    ldict = f.read()

location_dict = ast.literal_eval(ldict)

# set server parameters

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index_new.html')

@app.route('/cbot/<location>/', methods=['GET'])
def newdisplay(location):
    if request.method == 'GET':
        with open('/var/www/YOURHOST.YOURDOMAIN.EDU/cbot/{x}.txt'.format(x=location),mode='r') as f:
            o_raw = f.read()
        o_den = location_dict['{x}'.format(x=location)]['maxcap']
        offset = location_dict['{x}'.format(x=location)]['offset']
        o_num = int(o_raw)-int(offset)
        occ = int(o_num)/int(o_den)*100
        v = round(occ)
        loc = location_dict['{x}'.format(x=location)]['dispname']
        if 0 <= v < 75:
            return render_template('display_green.html',curocc=v,locn=loc,maxcap=o_den)
        elif 75 <= v <= 90:
            return render_template('display_yellow.html',curocc=v,locn=loc,maxcap=o_den)
        elif v > 90:
            return render_template('display_red.html',curocc=v,locn=loc,maxcap=o_den)
        elif v < 0:
            w = 0
            return render_template('display_green.html',curocc=w,locn=loc,maxcap=o_den)
        else:
            return render_template('display_green.html',curocc=v,locn=loc,maxcap=o_den)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

