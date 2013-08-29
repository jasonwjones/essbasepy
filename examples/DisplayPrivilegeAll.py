# Use the Essbase.py module. This statement is required to use Essbase within a Python script.
import Essbase

import sys

# script log
logFile = r'F:\Logs\DisplayPrivilegeAll.log'
sys.stderr = open(logFile, 'w')

# login to Essbase
esb = Essbase.Essbase()
esb.connect("userid", "password", "server")

# get all privileges
fOut = open(r'F:\Logs\DisplayPrivilegeAll.txt', 'w')
for holder in ("user", "group"):
    stmt = "display privilege %s all" % holder
    esb.do(stmt)
    for row in esb.rows():
        user, app, db, privilege, privType = row
        if privilege != "no_access":
            line = '\t'.join((user, app, db, privilege, str(privType))) + '\n'
            fOut.write(line)

# Disconnect from the Essbase server.
esb.disconnect()

fOut.close()
