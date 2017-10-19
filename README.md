## essbasepy – MaxL Python Module 

The MaxL Python Module, Essbase.py, provides access to Hyperion Essbase multi-dimensional databases from Python programs through MaxL. It is similar in function and usage to the Perl module Essbase.pm.

The Essbase Python module interfaces with Hyperion Essbase using a Python _ctypes_ module wrapper for the primary MaxL dll (essmaxl.dll or essmaxlu.dll). The ctypes module is standard in Python 2.5+. Versions of the wrapper are available for Essbase 6.5, for Essbase 7-11.2.1, and for Essbase 11.1.2.2.


## Distribution Notes

essbasepy files have now been consolidated down to a single distribution file. There are historical versions of essbasepy in for Essbase versions 6.5.x and 7.1.x in the legacy/ subfolder. Moving forward, they will not be maintained but will be part of this distribution for the foreseeable future.


## General Installation

1. Extract files
2. (Optional) If you want Unicode support, edit Essbase.py and change `ESS_UTF = False` to `ESS_UTF = True`
3. From the command line type: python setup.py install
4. Test using one or more of the supplied sample Essbase/Python scripts.


## Installation Sequence for 11.1.2.3/11.1.2.4

It took me awhile to get essbasepy to work on my Windows 2008 R2 64-bit server with Essbase (EPM) 11.1.2.3. After digging in, a solid sequence for getting essbasepy to work appears to be as follows. This assumes that your OS is 64-bit, and the Essbase/EPM software is 64-bit. 

  1. Download and install Python 2.7.5 64-bit from [python.org](http://www.python.org)
  2. Extract essbasepy files to a folder such as C:\essbasepy. You should be able to put this anywhere but my recommendation would be to put it in a low level folder that doesn't have spaces in it
  3. Configure your PATH. You should have the Python folder and the Essbase DLL folder in your PATH. The beginning of my server's PATH is ```C:\Python27_64;C:\Oracle\Middleware\EPMSystem11R1\common\EssbaseRTC-64\11.1.2.0\bin```
  4. Set the ESSBASEPATH environment variable. 
    1. On my Windows 2008 R2 machine this is set to ```%EPM_ORACLE_HOME%\products\Essbase\EssbaseServer```
    2. The EPM_ORACLE_HOME variable is set to ```C:\Oracle\Middleware\EPMSystem11R1```
  5. Install the Essbase Python module with ```python setup.py install```
  6. You should now be set. You should be able to run your own Python scripts that import the Essbase module from wherever you run them from
  

## Functions

- The following are similar in design to the functions supplied by the Essbase Perl Module: `connect()`, `do()`, `pop_msg()`, `fetch_desc()`, `fetch_row()`, `disconnect()`

- The following are extended utility functions that build upon the base functions above: 
 - `tdf()` - Returns a result set in the form of a tab-delimited file.
 - `msgs()` - Returns a message list that resulted from executing a MaxL statement.
 - `execute()` - Execute a MaxL statement and print resulting output.
 - `rows()` - Generator function to loop through Essbase output.


## Example Scripts

MaxlExec.py - execute a MaxL command and display the results
DisplayPrivilegeAll.py - display privileges of all users omitting databases with access of None
mdxtest.py - sample MaxL and MDX commands


## Common Issues

**maxl.MaxLInit(byref(inst)) returns 6 (Fatal Error) Essbase.isInitialized = False**

Ensure that the Essbase runtime client folder containing the MaxL dll is in your PATH. As of 11.1.2.1 the folder for 64-bit is ```%EPM_ORACLE_HOME%\common\EssbaseRTC-64\11.1.2.0\bin```, for 
32-bit it is ```%EPM_ORACLE_HOME%\common\EssbaseRTC\11.1.2.0\bin```


## History

### October 19, 2017

* Add enhancement to autodetect Essbase version and update an internal setting if needed. This should fix some instances where the wrapper worked fine for 11.1.2.4 but did not work out of the box for previous versions

### March 10, 2016

* HUGE number of update to cleanup Essbasepy for Python 3 and otherwise cleanup the code significantly
* HUGE thank you to Kevin (Github user nurzen) for all of these updates!
* If using Python 2.x you may need to use an older (the previous) version of Essbasepy 

### August 30, 2013

* essbasepy moved to GitHub
* Added new constants for 64-bit ULONGS (thanks to Stuart Ratner)
* Consolidated distribution down to one master distribution
* Updated documentation, added 11.1.2.3 install notes

### Legacy History (prior to GitHub/moving to August 30, 2013)

* Updated for MaxL api changes for 11.1.2.2, particularly for 64-bit support.
* Fixed a bug in fetch_desc() when no data returned (thanks to Chris Schulze for discovering this one).
* Added support for Unicode (thanks to Edward Delgado for many cycles of unit and integration testing).
* Changed method of locating MaxL library to (hopefully) make script Unix friendly.
* Added support for MaxL doubles.
* New generator function rows() which allows for simpler, more pythonic data access.
* New optional parameter timefmt for the execute() function. Defaults to original time.asctime() format.


## To Do

In no particular order:

 * I'd like enhance the code to make it more robust in the face of the environment not being configured correctly instead of failing with a seemingly unrelated error.


## Authors

Currently maintained by Jason Jones. Originally created by David Welden.


## License

essbasepy is licensed under the MIT License. 
