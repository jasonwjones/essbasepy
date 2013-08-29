# Use the Essbase.py module. This statement is required to use Essbase within a Python script.
import Essbase

import string
import sys
import time

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------

# start an Essbase session
if len(sys.argv) != 5:
	print "Usage: python %s <user> <pwd> <host> <command>" % sys.argv[0]
	sys.exit(0)

esb = Essbase.Essbase()
esb.connect(sys.argv[1], sys.argv[2], sys.argv[3])

# dump status messages
esb.msgs()

# execute statement
esb.execute(sys.argv[4])

# Disconnect from the Essbase server.
esb.disconnect()

