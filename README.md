switchport survey
=====================

When digging throught a spaghetti nest of wiring in a telco closet you might wonder, "How many of these cables are actually in use?"

This script is meant to help solve that problem and give you a roadmap to start cleaning things up.

----------
#### Requirement 1 - Logfiles with state changes

You'll want to have syslog captures from all your switches that include when a port goes up and down.
Example from a Cisco Switch "Oct 29 21:10:44.058 UTC: %LINK-3-UPDOWN: Interface GigabitEthernet0/8, changed state to up"

You want to have logs that go as far back as possible. (I typically only keep a few months of these types of logs.)

You can also get this from each switch. Cisco example 'show log' (but the bufffer may be small)

You can toss all these log files together collecting just the link state changes using something like this:

```
zgrep --no-filename floor6 syslog* | grep 'changed state to' | grep LINK > statechanges.log
```


----------
#### Requirement 2 - Current port state

You'll want to get the current port state for every port. (a port that's been up constantly won't trigger any up/down events)

An easy way to grab this from a cisco switch is to use 'show ip interface brief'

Example format: 'GigabitEthernet0/42    unassigned      YES unset  up                    up'

An ideal way to pull this down is to use a simple bash script and rancid.

```
#!/bin/bash

# assumes confdir holds your configs (and thus all switch names)
# our floor switches are named floorX-XX

HOMEDIR=/var/lib/rancid/
CONFDIR=$HOMEDIR/wmf/configs
DUMPDIR=$HOMEDIR/portstates

mkdir -p $DUMPDIR

# For each switch name, grab output
for file in $CONFDIR/floor*
do
    switch=`basename $file`
    echo $switch
    # run command on switch using rancid
    clogin -c 'show ip int br' $switch > $DUMPDIR/$switch.log
done
```

You can collect all the port states (only for GigabitEthernet ports we care about) using grep.
```
grep GigabitEthernet *.log > currentstate.log
```

----------
#### The Script

In this repo is a script that reads in these various log files and then prints out a summary of current states.

Usage:
./mergelogs.py statechange.log currentstate.log

It tries to 'do the right thing' by detecting which log it's reading from and organizing the data intelligently.

It spits out a csv importable output that you can drop in to a Googly doc for sharing.

Sample output: 

'floor6-02,GigabitEthernet0/01,up, 2014-09-25 07:54:42' -- means that this port is currently up and last changed on 9/25.

'floor6-01,GigabitEthernet0/37,down,' -- means that this port is currently down and that we have no log data about the last time it was up (depends on how far back your logs go)


YMMV -- read the code before you run it

----------
#### What to do next?

You need to decide what policy makes sense in your environment.

Maybe it's ok to turn down a port that hasn't been in use for 1 month, maybe it's not.

Common pitfalls: 
* Easily angered exec who's been away for a month and comes back to find a dead port.
* User who got an activated port on their first day, hasn't used it in 6 months, but will be annoyed if the wifi fails and they cannot use their wired jack

Work arounds:
* Make sure atleast one jack per desk is lit
* Use jack covers to mark 'dead' jacks

Have a lot of fun.







