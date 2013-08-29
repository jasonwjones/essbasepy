MaxL Python Module Essbase.py
=============================
David Welden
Deloitte Services LP

Released to the Public Domain. This module comes with no guarantees of any kind whatsoever. Use at your own risk.


Introduction
------------
The MaxL Python Module, Essbase.py, provides access to Hyperion Essbase multi-dimensional databases from Python programs through MaxL. It is similar in function and usage to the Perl module Essbase.pm. The Essbase Python module interfaces with Hyperion Essbase using a Python ctypes module wrapper for the primary MaxL dll (essmaxl.dll or essmaxlu.dll). The ctypes module is standard in Python 2.5 and may be downloaded for earlier versions from http://sourceforge.net/projects/ctypes. Versions of the wrapper are available for Essbase 6.5 and for Essbase 7.

Installation
------------
Prerequisites:
1. Extract files and from the command line type: python setup.py install
2. Test using one or more of the supplied sample Essbase/Python scripts.

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

Contributed Advanced Example Scripts
------------------------------------
The following are contributed scripts using Essbase.py for more advanced examples of Essbase administration:
essbase_appdb_session_.py - Check application and database load status for backup (contributed by Mike Nugent)
Essbase_user_functions_pp.py - Administer users and check Hyperion services (contributed by Mike Nugent)