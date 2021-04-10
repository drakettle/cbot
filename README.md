# cbot
A building wifi occupancy display based on Simon Little's COVID-Entry-Exit-system, to parse out device counts from Cisco's DNA Spaces firehose steam & present them as a very simple web display.

index.py -> this script pulls associatedClient counts out of the DNAS firehose stream by location & writes them to file

cbot.py -> this script runs a Flask server, reads the files written to by index.py, & presents wifi occupancy by location as a simple colour-coded web page

cbot.wsgi -> the Apache webserver needs this to interface with the Python script

location_dict.txt -> this file is a dictionary for location values ('area'= floor area, 'maxcap' = maximum occupancy for the location, 'dispname' = web page display name for the location, 'offset' = a value to account for persistent IoT devices in a location that would otherwise throw occupancy counts off; derived by taking an average of logged client counts during times when the location is known to be unoccupied (e.g., 0100-0300 daily for non-residential buildings locked up at night.
