MaxL Python Module Essbase.py
=============================
David Welden
Deloitte Services LP

Released to the Public Domain. This module comes with no guarantees of any kind whatsoever. Use at your own risk.


Introduction
------------
The MaxL Python Module, Essbase.py, provides access to Hyperion Essbase multi-dimensional databases from Python programs through MaxL. It is similar in function and usage to the Perl module Essbase.pm. The Essbase Python module interfaces with Hyperion Essbase using a Python ctypes module wrapper for the primary MaxL dll (essmaxl.dll or essmaxlu.dll). The ctypes module is standard in Python 2.5+. Versions of the wrapper are available for Essbase 6.5 and for Essbase 7.

Installation
------------
Prerequisites:
1. Extract files
2. (Optional) If you want Unicode support, edit Essbase.py and change:
        ESS_UTF = False
    to:
        ESS_UTF = True
3. From the command line type: python setup.py install
4. Test using one or more of the supplied sample Essbase/Python scripts.

Functions
---------
- The following are similar in design to the functions supplied by the Essbase Perl Module:
connect()
do()
pop_msg()
fetch_desc()
fetch_row()
disconnect()

- The following are extended utility functions that build upon the base functions above:
tdf() - Returns a result set in the form of a tab-delimited file.
msgs() - Returns a message list that resulted from executing a MaxL statement.
execute() - Execute a MaxL statement and print resulting output.
rows() - Generator function to loop through Essbase output.

Example Scripts
---------------
MaxlExec.py - execute a MaxL command and display the results
DisplayPrivilegeAll.py - display privileges of all users omitting databases with access of None
mdxtest.py - sample MaxL and MDX commands