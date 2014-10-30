#!/usr/bin/python

from dateutil import parser  # helpful for auto parsing dates
import re
import fileinput
import datetime

DEBUG=False

# Walk each line
lastchange={}
currentstate={}
for line in fileinput.input():

    if DEBUG:
        print '-'*80
        print line,


    # Get switch name (can be seperated by space or dot)
    m = re.search('(floor.+?)[ .]', line)
    if m:
        switch = m.group(1)
    else:
        switch = 'unknown'

    # Get port number (can be seperated by space or comma)
    m = re.search('([Ten]*GigabitEthernet.+?)[ ,]', line)
    if m:
        port = m.group(1)

        # catch and zero pad ports under 10
        (a,b) = port.split('/')
        port = "%s/%02d" % (a,int(b))
    else:
        port = 'unknown'

    switchport='%s %s' % (switch, port)

    if DEBUG:
        print switchport

    # We only care about the datestamp in statechange logs
    if 'changed state to' in line:
        # Get datestamp
        datestring=line[:15]
        date=parser.parse(datestring)

        # Is this a new switch port?
        if switchport not in lastchange:
            # log it
            lastchange[switchport] = date

        else: # We already have it, check datestamp
            if lastchange[switchport] < date: # get latest datestamp
                lastchange[switchport] = date

    else:
            if 'up' in line: state='up'
            else: state='down'
            currentstate[switchport] = state

# Walk all ports and print output in csv
for switchport in currentstate:
    (switch, port) = switchport.split()
    print "%s,%s,%s," % (switch, port, currentstate[switchport]),
    if switchport in lastchange:
        print lastchange[switchport],
    print ''
