import time
from win32wnet import WNetAddConnection2, WNetCancelConnection2, error
import cStringIO,operator

import os, Essbase, wmi,sys
from optparse import OptionParser
import win32serviceutil, win32service
import random
import zlib

RUNNING = win32service.SERVICE_RUNNING
STARTING = win32service.SERVICE_START_PENDING
STOPPING = win32service.SERVICE_STOP_PENDING
STOPPED = win32service.SERVICE_STOPPED

#Processes related to each Development and Production
#Set up as a dictionary
dict_dv={'TESTSERVER1':["OpenLDAP-slapd","beasvc SharedServices9WL8.1_SharedServices","beasvc easWL8.1_server1","beasvc HPDomainWL8.1_HPServer", \
			"Hyperion Interactive Reporting Base Service 1","Hyperion Interactive Reporting Data Access Service 1", \
			"Hyperion Interactive Reporting Service 1","HRCommSrv","HRReportSrv","HRSchedSrv","HRPrintSrv","HRWebSrv", \
			"beasvc WorkspaceWL8.1_WorkspaceApp","beasvc WebAnalysisWL8.1_WebAnalysisApp","Hyperion Licensing Service",'easTomcat5'],'TESTSERVER2':['EssbaseService']}

dict_ms={'PRODUCTIONSERVER1':['EssbaseService'],'PRODUCTIONSERVER2':["OpenLDAP-slapd","beasvc SharedServices9WL8.1_SharedServices","beasvc WebAnalysisWL8.1_WebAnalysisApp", \
						     "beasvc WorkspaceWL8.1_WorkspaceApp","Hyperion Licensing Service"], \
						     'PRODUCTIONSERVER3':["beasvc HPDomainWL8.1_HPServer","beasvc HyperionTMWL8.1_HTMServer","beasvc svpWL8.1_server1", \
								  "beasvc easWL8.1_server1"],'PRODUCTIONSERVER4':["Hyperion Interactive Reporting Base Service 1", \
														    'HRCommSrv','HRReportSrv','HRSchedSrv','HRPrintSrv']}

#List to ensure processes start in the correct order

production_order=[{'PRODUCTIONSERVER2':"beasvc SharedServices9WL8.1_SharedServices"},{'PRODUCTIONSERVER2':"OpenLDAP-slapd"},{'PRODUCTIONSERVER3':"beasvc easWL8.1_server1"},{'PRODUCTIONSERVER1':'EssbaseService'},{'PRODUCTIONSERVER3':"beasvc HPDomainWL8.1_HPServer"}]

development_order=[{'TESTSERVER1':"beasvc SharedServices9WL8.1_SharedServices"},{'TESTSERVER1':"OpenLDAP-slapd"},{'TESTSERVER1':"beasvc easWL8.1_server1"},{'TESTSERVER1':"beasvc HPDomainWL8.1_HPServer"},{'TESTSERVER2':"EssbaseService"}]



#Essbase class to interact with server via MaxL

class Essbase_status():
    def __init__(self):
	#Status obtained from Maxl display command
        self.Not_loaded=0
        self.Loading=1
        self.Loaded=2
        self.Unloading=3
        self.Essbase=Essbase.Essbase()
        self.hexStr='7bf255b64f46c12c0a240dbf5d4c02da1d805484'.decode('hex') #This is the hypadmin password coded to avoid clear text password Decodes to HyperionTest
        self.pWord=self.tinycode('nokawtg',self.hexStr,reverse=True) #This is the decryption code for password
	#Status obtained from Windows SC
        self.RUNNING = win32service.SERVICE_RUNNING
	self.STARTING = win32service.SERVICE_START_PENDING
	self.STOPPING = win32service.SERVICE_STOP_PENDING
	self.STOPPED = win32service.SERVICE_STOPPED
	
    def display_sessions(self):
	#Displays all Sessions
	firstmessage=0 #If do command fails, this setups place folder for error message
	listUser=[] #List of unique users
	dictUserSessions={} #Dictionary that maps unique user to sessions open
	dictSessions={} #Dictionary that maps Session to all related session values ie, user, session, login_time,...
	row='temp' #Creates row variable to prevent failure to unreferenced variable
	stat_level=self.Essbase.do('display session') #Run the MaxL command
	if stat_level<>0: #Indicates error encountered
            firstMessage=self.Essbase.pop_msg() # pulls first message
            print firstMessage # prints first message
            print self.Essbase.pop_msg() #Pops out any remaining messages. If none, they none is returned
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
        if stat_level==0: #No error
	    while type(row)!=type(None): #Pulls all returned rows #The remaining code is to populate listUser, dictUserSessions, dictSessions
		row=self.Essbase.fetch_row() 
		if row==None:break
		if '%s' % long(row[1])!='0': #The session ID of 0 (Zero) is not included. This represents the script that made the connection
		    if row[0] not in listUser:
			listUser.append(row[0])
			dictUserSessions[row[0]]=['%s' % long(row[1])]
		    else:
			tempList=dictUserSessions[row[0]]
			tempList.append('%s' % long(row[1]))
			dictUserSessions[row[0]]=tempList
		    dictSessions['%s' % long(row[1])]=row
		    #print row
		    listTemp=[]
	return listUser, dictUserSessions, dictSessions
    
    def display_session_id(self,sessionID):
	#This is used to confirm that session has been logged out
	listuser, dictUserSession, dictSession=self.display_sessions() #Preforms a display session 
	try:
	    return dictSession[sessionID] #Looks for the requested ID
	except KeyError:
	    print "%s ID not found" % sessionID
	    return None

            
    def connect(self,user,password,server):
	#This preforms the connection to the Essbase Server
	#Essbase.py was modified to return the status number back to the this script
        stat_level=self.Essbase.connect(user,password,server)
	if stat_level==0:
	    print "Connected"
	else:
	    print "Not Connected Reason code: %s" % stat_level

    def disconnect(self):
	#Disconnect from the Essbase server
        self.Essbase.disconnect()
        print "Disconnected"
    def tinycode(self,key, text, reverse=False):
	#This is used to decrypt the hypadmin password from clear text.
	#Only to prevent using plain clear text
        rand = random.Random(key).randrange
        if not reverse:
            text = zlib.compress(text)
        text = ''.join([chr(ord(elem)^rand(256)) for elem in text])
        if reverse:
            text = zlib.decompress(text)
        return text
    
    def service_info(self,action, machine, service):
	#Interacts with the Window's service controller
	#The netconnection must be completed first
	#If netconnection is not done first, a Permission denied may return from SC controller
        if action == 'stop': 
            win32serviceutil.StopService(service, machine)
            print '%s stopped successfully' % service
        elif action == 'start': 
            win32serviceutil.StartService(service, None,machine)
            print '%s started successfully' % service
        elif action == 'restart': 
            win32serviceutil.RestartService(service, machine)
            print '%s restarted successfully' % service
        elif action == 'status':
	    #print win32serviceutil.QueryServiceStatus(service, machine)
	    retStatus=win32serviceutil.QueryServiceStatus(service, machine)[1]
            if retStatus == self.RUNNING:  # scvType, svcState, svcControls, err, svcErr, svcCP, svcWH
		print "%s on %s is running" % (service,machine)
                return self.RUNNING
            elif retStatus == self.STARTING:
		print '%s on %s is STARTING' % (service,machine)
                return self.STARTING
	    elif retStatus == self.STOPPING:
		print '%s on %s is STOPPING' % (service,machine)
		return self.STOPPING
	    elif retStatus == self.STOPPED:
		print '%s on %s is STOPPED***************' % (service,machine)
		return self.STOPPED
	    else:
		print "Failed to get status for %s on %s" % (service,machine)
    def logout_session(self,sessionID,force=False):
	#Logs out the requested session
	#Also includes ability to use the MaxL force term
	if force:
	    stat=self.Essbase.do('alter system logout session %s force' % sessionID)
	else:
	    stat=self.Essbase.do('alter system logout session %s' % sessionID)
	print stat
    def kill_request(self,sessionID):
	#Kills the specified request
	stat=self.Essbase.do('alter system kill request %s' % sessionID)
	print stat
    def shutdown_system(self):
	#Shuts down Essbase server
	#Also possible to use SC controller to do this
	stat=self.Essbase.do('alter system shutdown')
	print stat

    def netaddconnection(self,server,user,password):
	#This allows any user to manipulate the server using different credentials
	if user=='hypadmin':
	    password=self.pWord #Specifying password using hypadmin is not needed. Password is obtained through script
	user='global\\%s' % user
	try:
	    WNetAddConnection2(0,None,'\\\\%s' % server,None,user,password)
	except Exception, err:
	    if isinstance(err,error):
		print err
		if err[0]==1219:
		    self.netcancelconnection(server)
		    WNetAddConnection2(0,None,'\\\\%s' % server,None,user,password)
		    
    def netcancelconnection(self,server):
	#This is for housekeeping to close connection to server
	try:
	    WNetCancelConnection2('\\\\%s' % server, 0, 0)
	except Exception, err:
	    if isinstance(err,error):
		print err
		if err[0]==2250:
		    pass

#The purpose is to open the Essbase log to confirm Essbase.exe actually started
#The SC controller will report back that the service has started, but it may shutdown due to a corrupted SEC file
#or License server being unavailable
def BackwardsReader(file, BLKSIZE = 4096):
    """Read a file line by line, backwards"""

    buf = ""
    file.seek(-1, 2)
    lastchar = file.read(1)
    trailing_newline = (lastchar == "\n")
    
    while 1:
        newline_pos = buf.rfind("\n")
        pos = file.tell()
        if newline_pos != -1:
            # Found a newline
            line = buf[newline_pos+1:]
            buf = buf[:newline_pos]
            if pos or newline_pos or trailing_newline:
                line += "\n"
            yield line
        elif pos:
            # Need to fill buffer
            toread = min(BLKSIZE, pos)
            file.seek(-toread, 1)
            buf = file.read(toread) + buf
            file.seek(-toread, 1)
            if pos == toread:
                buf = "\n" + buf
        else:
            # Start-of-file
            return		
def essbase_log_reader(server):
    #Opens Essbase log in read-only mode
    #netconnection was be completed first or Access Denied may occur
    essbase_log=open(r'\\%s\d$\Hyperion\AnalyticServices\ESSBASE.LOG' % server,'rb')
    line=essbase_log.readline()
    try:
	if not line:
	    raise EOFError
	else:
	    print "last 10 Essbase Log lines"
	    counter=0
	    rLine=BackwardsReader(essbase_log)
	    listrLine=[]
	    while counter<21:
		tempLine=rLine.next()
		if tempLine<>'':
		    listrLine.append(tempLine[:-2])
		counter=counter+1
	    listrLine.reverse()
	    for outLine in listrLine:
		print outLine
	    essbase_log.close()
	    if 'Hyperion OLAP Server - started' in listrLine:
		print "started FINALLY!!!"
		return 1
	    else:
		print "STOPPED"
		return 0
    except EOFError:
	print "Essbase Log file empty"
	essbase_log.close()
	counter=0
	return 0

    
#Imported this code from Activestate Python cookbook##############################
#Creates table for display session output
def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x:x):
    """Indents a table by column.
       - rows: A sequence of sequences of items, one sequence per row.
       - hasHeader: True if the first row consists of the columns' names.
       - headerChar: Character to be used for the row separator line
         (if hasHeader==True or separateRows==True).
       - delim: The column delimiter.
       - justify: Determines how are data justified in their column. 
         Valid values are 'left','right' and 'center'.
       - separateRows: True if rows are to be separated by a line
         of 'headerChar's.
       - prefix: A string prepended to each printed row.
       - postfix: A string appended to each printed row.
       - wrapfunc: A function f(text) for wrapping text; each element in
         the table is first wrapped by this function."""
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in map(None,*newRows)]
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = map(None,*reduce(operator.add,logicalRows))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + \
                                 len(delim)*(len(maxWidths)-1))
    # select the appropriate justify method
    justify = {'center':str.center, 'right':str.rjust, 'left':str.ljust}[justify.lower()]
    output=cStringIO.StringIO()
    if separateRows: print >> output, rowSeparator
    for physicalRows in logicalRows:
        for row in physicalRows:
            print >> output, \
                prefix \
                + delim.join([justify(str(item),width) for (item,width) in zip(row,maxWidths)]) \
                + postfix
        if separateRows or hasHeader: print >> output, rowSeparator; hasHeader=False
    return output.getvalue()

# written by Mike Brown
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
def wrap_onspace(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line[line.rfind('\n')+1:])
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

import re
def wrap_onspace_strict(text, width):
    """Similar to wrap_onspace, but enforces the width constraint:
       words longer than width are split."""
    wordRegex = re.compile(r'\S{'+str(width)+r',}')
    return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(),width),text),width)

import math
def wrap_always(text, width):
    """A simple word-wrap function that wraps text on exactly width characters.
       It doesn't split the text in words."""
    return '\n'.join([ text[width*i:width*(i+1)] \
                       for i in xrange(int(math.ceil(1.*len(text)/width))) ])

#END IMPORTED CODE From Activestate cookbook####################################

def main():
    #Added this to pull Display session and output in table format
    listUser, dictUserSession, dictSession=objEssbase.display_sessions()

    for session in dictSession.keys():
	if dictSession[session][10]=='in_progress':
		print dictSession[session]
		#objEssbase.kill_request(session)
    #Pretty Print Area#########
    strFull=""
    strLine=""
    for User in dictUserSession.keys():
	    #if dictSession[session][3]=='' and dictSession[session][8]=='workfl' and session<>'2933915598':
	#print dictSession[session]
	for Session in dictUserSession[User]:
	    for entry in dictSession[Session]:
		strLine='%s%s,' % (strLine,entry)
	    strFull='%s%s\r\n' % (strFull,strLine[:-1])
	    strLine=''
    #Pretty Print
    labels = ('user', 'session', 'login_time', 'application', 'database', 'db_connect_time', 'request', 'request_time', 'connection_source', 'connection_ip','request_state')
    data=strFull
    #print data
    print 'Without wrapping function\n'
    rows = [row.strip().split(',')  for row in data.splitlines()]
    print indent([labels]+rows, hasHeader=True)
		


if __name__=='__main__':
    #Set the desired Essbase server
    #EssSrvr='TESTSERVER2'
    EssSrvr='PRODUCTIONSERVER1'
    #sets the dictionary to use based on server value
    if EssSrvr=='TESTSERVER2':
	dict_use=dict_dv
    else:
	dict_use=dict_ms
	
    objEssbase=Essbase_status() #Create class instance
    for Srvr in dict_use.keys(): #Creates netaddconnections based development or production servers
	objEssbase.netaddconnection(Srvr,'hypadmin',None)
    if objEssbase.service_info('status',EssSrvr,'EssbaseService')==RUNNING: #Checks to see if Essbase is running before making a connection
	print "Essbase is running"
	objEssbase.connect('hypadmin',objEssbase.pWord,EssSrvr) #Makes connection to Essbase


    main()
#    for Srvr in dict_use.keys(): #House keeping disconnection from servers
#	objEssbase.netcancelconnection(Srvr)
#    objEssbase.disconnect() #Housekeeping disconnect from Essbase
    
'''Sample usage
Script ran directly

Python 2.5.2 (r252:60911, Mar 27 2008, 17:57:18) [MSC v.1310 32 bit (Intel)]
Type "help", "copyright", "credits" or "license" for more information.
>>> 
Evaluating Essbase_user_functions_pp.py
Essbase Init status: 0
Essbase isInitialized: True
EssbaseService on PRODUCTIONSERVER1 is running
Essbase is running
Connected
Without wrapping function

user     | session      | login_time | application | database | db_connect_time | request | request_time | connection_source  | connection_ip  | request_state
--------------------------------------------------------------------------------------------------------------------------------------------------------------
hypadmin | 1593835454.0 | 14694.0    |             |          | 0.0             | none    | 0.0          | PRODUCTIONSERVER2  | 192.168.1.5    |              
hypadmin | 2042625892.0 | 6045.0     |             |          | 0.0             | none    | 0.0          | CLIENT3            | 192.168.1.4    |              
hypadmin | 150994787.0  | 15527.0    | APP1        | DB1      | 15526.0         | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 867172189.0  | 6956.0     | APP2        | DB2      | 6955.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 602931036.0  | 6879.0     | APP2        | DB2      | 6878.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 3685744475.0 | 6525.0     | APP2        | DB2      | 6524.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 3111124826.0 | 6357.0     | APP1        | DB1      | 6356.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
USER1    | 1283456870.0 | 17112.0    | APP3        | DB3      | 17108.0         | none    | 0.0          | CLIENT1            | 192.168.1.2    |              
USER1    | 273678181.0  | 16817.0    | APP3        | DB3      | 16816.0         | none    | 0.0          | CLIENT1            | 192.168.1.2    |              
USER1    | 2825912161.0 | 15054.0    | APP3        | DB3      | 15053.0         | none    | 0.0          | CLIENT1            | 192.168.1.2    |              
USER2    | 3766484832.0 | 12820.0    | APP4        | DB3      | 12816.0         | none    | 0.0          | CLIENT2            | 192.168.1.3    |             
USER2    | 2592079711.0 | 12477.0    | APP4        | DB3      | 12475.0         | none    | 0.0          | CLIENT2            | 192.168.1.3    |   

calling displaysession to return list and dictionaries

>>> listuser, dictUserSession, dictSession=objEssbase.display_sessions()
>>> listuser
['USER1', 'USER2', 'hypadmin']
>>> dictUserSession
{'hypadmin': ['1593835454', '2042625892', '150994787', '867172189', '602931036', '3685744475', '3111124826'], 'USER1': ['1283456870', '273678181', '2825912161'], 'USER2': ['3766484832', '2592079711']}
>>> dictSession
{'2825912161': ['USER1', 2825912161.0, 15170.0, 'APP3', 'DB3', 15169.0, 'none', 0.0, 'CLIENT1', '192.168.1.2', ''], '1593835454': ['hypadmin', 1593835454.0, 14810.0, '', '', 0.0, 'none', 0.0, 'PRODUCTIONSERVER2', '192.168.1.5', ''], '3685744475': ['hypadmin', 3685744475.0, 6641.0, 'APP2', 'DB2', 6640.0, 'none', 0.0, 'PRODUCTIONSERVER2', '192.168.1.52', ''], '602931036': ['hypadmin', 602931036.0, 6995.0, 'APP2', 'DB2', 6994.0, 'none', 0.0, 'PRODUCTIONSERVER2', '192.168.1.52', ''], '2592079711': ['USER2', 2592079711.0, 12593.0, 'APP4', 'DB3', 12591.0, 'none', 0.0, 'CLIENT2', '192.168.1.3', ''], '3766484832': ['USER2', 3766484832.0, 12936.0, 'APP4', 'DB3', 12932.0, 'none', 0.0, 'CLIENT2', '192.168.1.3', ''], '2042625892': ['hypadmin', 2042625892.0, 6161.0, '', '', 0.0, 'none', 0.0, 'CLIENT3', '192.168.1.4', ''], '3111124826': ['hypadmin', 3111124826.0, 6473.0, 'APP1', 'DB1', 6472.0, 'none', 0.0, 'PRODUCTIONSERVER1', '192.168.1.52', ''], '150994787': ['hypadmin', 150994787.0, 15643.0, 'APP1', 'DB1', 15642.0, 'none', 0.0, 'PRODUCTIONSERVER1', '192.168.1.52', ''], '1283456870': ['USER1', 1283456870.0, 17228.0, 'APP3', 'DB3', 17224.0, 'none', 0.0, 'CLIENT1', '192.168.1.2', ''], '273678181': ['USER1', 273678181.0, 16933.0, 'APP3', 'DB3', 16932.0, 'none', 0.0, 'CLIENT1', '192.168.1.2', ''], '867172189': ['hypadmin', 867172189.0, 7072.0, 'APP2', 'DB2', 7071.0, 'none', 0.0, 'PRODUCTIONSERVER1', '192.168.1.52', '']}
>>> 

Logging out all session tied to USER1
>>> for session in dictUserSession['USER1']:
... 	objEssbase.logout_session(session)
... 
0
0
0
>>> 

Confirming that one USER1 session is gone and one hypadmin session still exists
>>> objEssbase.display_session_id('2825912161')
2825912161 ID not found
>>> objEssbase.display_session_id('1593835454')
['hypadmin', 1593835454.0, 15051.0, '', '', 0.0, 'none', 0.0, 'PRODUCTIONSERVER2', '192.168.1.5', '']
>>> 

Querying service on PRODUCTIONSERVER2

>>> for Service in dict_use['PRODUCTIONSERVER2']:
... 	objEssbase.service_info('status','PRODUCTIONSERVER2', Service)
... 
beasvc HPDomainWL8.1_HPServer on PRODUCTIONSERVER2 is running
4
beasvc HyperionTMWL8.1_HTMServer on PRODUCTIONSERVER2 is running
4
beasvc svpWL8.1_server1 on PRODUCTIONSERVER2 is running
4
beasvc easWL8.1_server1 on PRODUCTIONSERVER2 is running
4
>>> 

The log reader is pulling back the last 20 lines from the essbase.log
It was added to find the string 'Hyperion OLAP Server - started'
Only needed when Essbase is started. That is why it printed STOPPED at the bottom

>>> essbase_log_reader('PRODUCTIONSERVER1')
last 10 Essbase Log lines
Received client request: MaxL: Define (from user [hypadmin])

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1051001)
Received client request: MaxL: Fetch (from user [hypadmin])

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1243003)
Record(s) fetched

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1051001)
Received client request: MaxL: Describe (from user [hypadmin])

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1243002)
Output columns described

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1051001)
Received client request: MaxL: Define (from user [hypadmin])

[Tue Jun 17 20:04:19 2008]Local/ESSBASE0///Info(1051001)
Received client request: MaxL: Fetch (from user [hypadmin])


STOPPED
0

The main() function allows a quick pretty print for the display application

>>> main()
Without wrapping function

user     | session      | login_time | application | database | db_connect_time | request | request_time | connection_source  | connection_ip  | request_state
--------------------------------------------------------------------------------------------------------------------------------------------------------------
hypadmin | 1593835454.0 | 17131.0    |             |          | 0.0             | none    | 0.0          | PRODUCTIONSERVER2  | 192.168.1.5    |              
hypadmin | 2042625892.0 | 8482.0     |             |          | 0.0             | none    | 0.0          | CLIENT3            | 192.168.1.4    |              
hypadmin | 150994787.0  | 17964.0    | APP1        | DB1      | 17963.0         | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 867172189.0  | 9393.0     | APP2        | DB2      | 9392.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 602931036.0  | 9316.0     | APP2        | DB2      | 9315.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 3685744475.0 | 8962.0     | APP2        | DB2      | 8961.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
hypadmin | 3111124826.0 | 8794.0     | APP1        | DB1      | 8793.0          | none    | 0.0          | PRODUCTIONSERVER1  | 192.168.1.52   |              
USER2    | 3766484832.0 | 15257.0    | APP4        | DB3      | 15253.0         | none    | 0.0          | CLIENT2            | 192.168.1.3    |              
USER2    | 2592079711.0 | 14914.0    | APP4        | DB3      | 14912.0         | none    | 0.0          | CLIENT2            | 192.168.1.3    |              
'''
