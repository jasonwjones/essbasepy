
from __future__ import generators
from time import localtime, sleep
import os, Essbase, wmi,sys
from optparse import OptionParser
import win32serviceutil
import random
import zlib
from win32wnet import WNetAddConnection2, WNetCancelConnection2, error
import wmi


listTemp=[]
listComplete=[]
dictApps_Dbs={}
strDate=localtime()

parser= OptionParser()

parser.add_option("-s","--server",type="string",dest="Server",default="testserver",help="Enter the Essbase Server name.")
parser.add_option("-f","--files",type="string",dest="bDataFiles",default="F",help="Data files to be backed up?")
parser.add_option("-c","--clear",type="string",dest="bClear",default="F",help="Log files to be clear?")
parser.add_option("-r","--running",type="string",dest="bRunning",default="F",help="Shutdown running Application/Database for backup?")

#Command line arguments to process before backup is started
(options, args) = parser.parse_args()

print options.Server
print options.bDataFiles
print options.bClear
print options.bRunning

bRunning=options.bRunning.upper()
bClear=options.bClear.upper()
bDataFiles=options.bDataFiles.upper()

#This resets the log clear and data backup false to False is the running app/db cannot be shutdown
if bRunning=='F':
    bClear='F'
    bDataFiles='F'

#Creates List of file extensions to search before backup purposes
#Depending on command line arguments and Essbase running state
if bDataFiles=='F':
    if bRunning=='F':
        extensionList=["db","otl","csc","rul","app"]
    else:
        extensionList=["esm","tct","db","otl","csc","rul","app","log"]
else:
    if bRunning=='F':
        extensionList=["db","otl","csc","rul","app"]
    else:
        extensionList=["ind","pag","esm","tct","db","otl","csc","rul","app","log"]

#
hexStr='7bf255b64f46c12c0a240dbf5d4c02da1d805484'.decode('hex') #Decodes to HyperionTest



class Essbase_appdbs_status():
    def __init__(self):
        self.Not_loaded=0
        self.Loading=1
        self.Loaded=2
        self.Unloading=3
        self.Essbase=Essbase.Essbase()
	self.hexStr='7bf255b64f46c12c0a240dbf5d4c02da1d805484'.decode('hex')#This hextstring decodes to: HyperionTest
	self.pWord=self.tinycode('nokawtg',self.hexStr,reverse=True)
    def essbase_service(self,machine):
	#Uses the SC Query to obtain Essbase running state and return a 1 or 0
        service="EssbaseService"
        if win32serviceutil.QueryServiceStatus(service, machine)[1] == 4:        
            print "Essbase is running!!!!!!!!!!!!!!!!"
            return 1
        else:
            return 0
            
    def display_application(self,app):
	#Checks the application status
        firstMessage=0
        #print ':%s:' % app
        stat_level=self.Essbase.do('display application %s' % app)
        if stat_level<>0:
            firstMessage=self.Essbase.pop_msg()
            print firstMessage
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
        if stat_level==0:
            row=self.Essbase.fetch_row()
            #print row
            result=row[14]
            if result==self.Loaded:
                print "App: %s is Loaded" % app
                return self.Loaded
            elif result==self.Not_loaded:
                print "App: %s is NOT Loaded" % app
                return self.Not_loaded
            elif result==self.Loading:
                print "App: %s is Loading" % app
            elif result==self.Unloading:
                print "App: %s is Unloading" % app
        elif firstMessage[0]<>1051030:
            result=self.Not_loaded
            
    def connect(self,user,password,server):
	#connect to Essbase
	if user.lower()=='hypadmin':password=self.pWord #If hypadmin is used, pull the password internally
        self.Essbase.connect(user,password,server)

    def disconnect(self):
	#housekeeping disconnect from Essbase
        self.Essbase.disconnect()
        
    def display_database(self,dbs):
	#Checks the database status
        firstMessage=0
        if dbs=="TestApp.Direct":dbs="TestApp.'Direct'" #This was need to place single quotes around the MaxL reserved word: Direct
        stat_level=self.Essbase.do("display database %s" % dbs)
        if stat_level<>0:
            firstMessage=self.Essbase.pop_msg()
            print firstMessage
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
        if stat_level==0:
            row=self.Essbase.fetch_row()
            result=row[31]
            if result==self.Loaded:
                print "DBS: %s is Loaded" % dbs
                return self.Loaded
            elif result==self.Not_loaded:
                print "DBS: %s is NOT Loaded" % dbs
                return self.Not_loaded
            elif result==self.Loading:
                print "DBS: %s is Loading" % dbs
            elif result==self.Unloading:
                print "DBS: %s is Unloading" % dbs
        elif firstMessage[0]<>1051030:
            result=self.Not_loaded
    def unload_db(self,app,dbs):
	#Unload database. Used before backup starts
        if dbs=="Direct":dbs="'Direct'" #This was need to place single quotes around the MaxL reserved word: Direct
        stat_level=self.Essbase.do('alter application %s unload database %s' % (app,dbs))
        sleep(5)
        return stat_level

    def load_db(self,app,dbs):
	#Load database after backup complete
        if dbs=="Direct":dbs="'Direct'" #This was need to place single quotes around the MaxL reserved word: Direct
        stat_level=self.Essbase.do('alter application %s load database %s' % (app,dbs))
        sleep(5)
        return stat_level

    def unload_app(self,app):
	#Unload app before backup and clearing log file
        stat_level=self.Essbase.do('alter system unload application %s' % (app))
        sleep(5)
        return stat_level

    def load_app(self,app):
	#Load app after backup and log clear completed
        stat_level=self.Essbase.do('alter system load application %s' % (app))
        sleep(5)
        return stat_level
    def display_application_all(self):
	#This creates two lists. One list for all Running apps
	#Second list for all stopped apps
        listRunning=[]
        listStopped=[]

        firstMessage=0
        stat_level=self.Essbase.do("display application all")
        
        if stat_level<>0:
            firstMessage=self.Essbase.pop_msg()
            print firstMessage
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
        elif stat_level==0:
            row=self.Essbase.fetch_row()
            while type(row)!=type(None):
                if row[14]==2:
                    listRunning.append(row[0])
                else:
                    listStopped.append(row[0])
		try:
		    row=self.Essbase.fetch_row()
		except AttributeError:
		    break
        return listRunning, listStopped
    
    def display_database_all(self):
    	#This creates two lists. One list for all Running databases
	#Second list for all stopped databases
        listRunning=[]
        listStopped=[]

        firstMessage=0
        stat_level=self.Essbase.do("display database all")
        
        if stat_level<>0:
            firstMessage=self.Essbase.pop_msg()
            print firstMessage
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
            print self.Essbase.pop_msg()
        elif stat_level==0:
	    row=self.Essbase.fetch_row()
            while type(row)!=type(None):
                if row[31]==2:
                    listRunning.append('%s:%s' % (row[0],row[1]))
                else:
                    listStopped.append('%s:%s'  % (row[0],row[1]))
		try:
		    row=self.Essbase.fetch_row()
		except AttributeError:
		    break
        return listRunning, listStopped
    
    def netaddconnection(self,server,user,password):
	#Creates a connection to the server using specified creditentials
	if user=='hypadmin':
	    password=self.pWord
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
	#Housekeeping to shutdown the server connection
	#If this is not run, and future connections will use this existing
	#connection.
	try:
	    WNetCancelConnection2('\\\\%s' % server, 0, 0)
	except Exception, err:
	    if isinstance(err,error):
		print err
		if err[0]==2250:
		    pass
    
    def tinycode(self,key, text, reverse=False):#Encrypt/Decrypt code
        rand = random.Random(key).randrange
        if not reverse:
            text = zlib.compress(text)
        text = ''.join([chr(ord(elem)^rand(256)) for elem in text])
        if reverse:
            text = zlib.decompress(text)
        return text
    
    def app_process_id(self,server,luser,pword):
	#This code uses WMI interface to obtain the application PIDs
	#A list is returned with the PIDs as numeric values
	lstProcess_ID=[]
	if luser=='hypadmin':
	    pword=self.pWord
	luser='global\\%s' % luser
	c=wmi.WMI(computer=server,user=luser,password=pword)
	for process in c.Win32_Process(name='esssvr.exe'):
	    #print process.ProcessID, process.Name
	    lstProcess_ID.append(process.ProcessID)
	return lstProcess_ID
    
    def BackwardsReader(self,file, BLKSIZE = 4096):
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
    def find_application_process_id(self,Srvr,ID):
	#match application to process id from Essbase Log
	#The numberic ID must be converted to a string first. Such as str(ID)
	#The Essbase log is read in reverse to find the ID
	essbase_log=open(r'\\%s\d$\Hyperion\AnalyticServices\ESSBASE.LOG' % Srvr,'rb')
 	rline=self.BackwardsReader(essbase_log)
	strApp=''
 	while 1:
 		tempLine=rline.next()
 		if tempLine.find(ID)<>-1:
 			print tempLine
			strApp=tempLine[tempLine.find('[')+1:tempLine.find(']')]
 			break
 	del(rline)
 	essbase_log.close()
	return strApp,ID

def dirwalk(dir,extension):#finds all files matching the file extensions specified
    "walk a directory tree, using a generator"
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath,extension):  # recurse into subdir
                yield x
        else:
            if f[-3:].lower()==extension:
                yield [dir,f]
                
def compressFiles(archiveName,fileList7z):
    #7z compressor is used
    #This gives a much higher compression ratio, but speed is slower on compression
    #This function is hard-coded to the D:\Hyperion_files\archive directory
    sts=os.system('C:\\Pstools\\7z.exe a -t7z d:\\Hyperion_files\\%s.7z @%s' % (archiveName,fileList7z))
    return sts

def storeFiles(year,month,day):
    #The 7z compressor is used, but in "store" mode. No compression is used.
    #All of the file lists are added to this archive
    sts=os.system('C:\\Pstools\\7z.exe a -t7z -mx0 d:\\Hyperion_files\\archive\\%s_%s_%s.7z d:\\Hyperion_files\\*.7z d:\\Hyperion_filelst\\all.log' % (year,month,day))
    return sts

def completedFiles(strKey):
    #Once the application and related databases are archived, the filelist used to create them is deleted from the D:\Hyperion_filelst directory
    #The Hyperion_filelst directory will be empty when the compression is complete.
    #Any file list that remain means that compression may have failed
    print '%s.7z is complete' % strKey
    listComplete.append('%s.7z' % strKey)
    os.remove('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey)

if __name__=='__main__':
    outputFile=open('d:\\Hyperion_filelst\\all.log','wb') #Hardcoded output file for all the file list entries
    stat=Essbase_appdbs_status() #Initialize the class
    
    for strExtension in extensionList: #Start creating the file lists. These file list are sent to 7z for compression
        for thefiles in dirwalk('d:\\Hyperion\\AnalyticServices\\app\\',strExtension):
            if strExtension.lower() in ["app","log"]: #This use the database name of: all for file not related to a specific datbase
                appName=thefiles[0][thefiles[0].rfind("\\")+1:]
                dbName="all"
            else:
                appName=thefiles[0][thefiles[0].rfind("\\",1,thefiles[0].rfind("\\")-2)+1:thefiles[0].rfind("\\")]
                dbName=thefiles[0][thefiles[0].rfind("\\")+1:]
            if "%s.%s" % (appName,dbName) not in dictApps_Dbs.keys():#Creates a dictionary using the App.DB name as a key. The value is a list.
                dictApps_Dbs["%s.%s" % (appName,dbName)]=[thefiles[0] + "\\" + thefiles[1]] #This is the first list entry
            else:
                listTemp=dictApps_Dbs["%s.%s" % (appName,dbName)]#Additional list entries are added by pulling the list out to a temp List,
                listTemp.append(thefiles[0] + "\\" + thefiles[1])#appending the new entry, and reseting the dictionary to the updated list
                dictApps_Dbs["%s.%s" % (appName,dbName)]=listTemp
            outputFile.write('%s\\%s!%s\r\n' % (thefiles[0],thefiles[1],thefiles[1]))#Housekeeping log entry to the all.log
            outputFile.flush()
    #EssbaseRelated Backup Here
    #These files are handled different, since they do not relate to the app\ directory
    appName="Essbase"
    dbName="all"
    #This is the dictionary for all the Essbase related files
    essBaseDict={'ESSBASE.BAK':'d:\\Hyperion\\AnalyticServices\\bin\\ESSBASE.BAK','essbase.cfg':'d:\\Hyperion\\AnalyticServices\\bin\\essbase.cfg','essbase.log':'d:\\Hyperion\\AnalyticServices\\essbase.log','ESSBASE.SEC':'d:\\Hyperion\\AnalyticServices\\bin\\ESSBASE.SEC'}

    if stat.essbase_service(options.Server)==1: #essbase is running, cannot backup LOG or SEC file
        del essBaseDict['ESSBASE.SEC']#This removes the key:value pairs for file that cannot be backuped or cleared when Essbase is running
        del essBaseDict['essbase.log']
        for strItem in essBaseDict.keys():
            outputFile.write('%s\\!%s\r\n' % (essBaseDict[strItem],strItem))#Housekeeping entry to the all.log
            outputFile.flush()
            if "%s.%s" % (appName,dbName) not in dictApps_Dbs.keys():#Same dictionary entry as the Apps/Databases, but for Essbase itself
                dictApps_Dbs["%s.%s" % (appName,dbName)]=["%s" % essBaseDict[strItem]]
            else:
                listTemp=dictApps_Dbs["%s.%s" % (appName,dbName)]
                listTemp.append("%s" % essBaseDict[strItem])
                dictApps_Dbs["%s.%s" % (appName,dbName)]=listTemp
    else:#Since Essbase is not running, all files can be backed up
        for strItem in essBaseDict.keys():
            outputFile.write('%s\\!%s\r\n' % (essBaseDict[strItem],strItem))
            outputFile.flush()
            if "%s.%s" % (appName,dbName) not in dictApps_Dbs.keys():
                dictApps_Dbs["%s.%s" % (appName,dbName)]=["%s" % essBaseDict[strItem]]
            else:
                listTemp=dictApps_Dbs["%s.%s" % (appName,dbName)]
                listTemp.append("%s" % essBaseDict[strItem])
                dictApps_Dbs["%s.%s" % (appName,dbName)]=listTemp

    listKeys=dictApps_Dbs.keys() #Creates list for the App.Database keys
    listKeys.sort()#Sorts the list so all Apps and databases are grouped together
    
    if stat.essbase_service(options.Server)==1: #Essbase is running, so many additional checks/procedures will be needed
	#One major check is to ensure the "Application" actually is an Essbase app/database. Sometimes a folder is created under the app\ folder
	#but is NOT an actual Essbase application.
        pword=tinycode('nokawtg',hexStr,reverse=True) #Obtain the password
        stat.connect('hypadmin',pword,options.Server)#Connect to Essbase
        for strKey in listKeys:
            print strKey
            fileList=open('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey,'wb')
            for strPath in dictApps_Dbs[strKey]:
                print strPath
                fileList.write('"%s"\r\n' % strPath)
                fileList.flush()
            fileList.close()
            #run compression here
            #Before running the Log compress, check application status
            if strKey.find('$')==-1: #File system included a directory prepended with an $ sign. This directory is handled separately
                if strKey.split('.')[1]=='all':
                    App_stat=stat.display_application(strKey.split('.')[0])
                    print App_stat
                    if App_stat==2 and bRunning<>'F': #check to see if application is running and can be shutdown
                        if stat.unload_app(strKey.split('.')[0])==0: #Unloading application here
                            if compressFiles(strKey,fileList.name)==0: #File list is sent to 7z for compression if 0, then successful
                                fileListLines=open('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey,'rb').readlines() #Opens file list to locate the .log file
                                for itemLines in fileListLines:#scans the filelist
                                    if itemLines.lower().find('log')<>-1 and bClear=="T": #Check to see if a Application log exists and if it should be cleared
                                        tempFile=open(itemLines[1:-3],'wb') #This quickly clears the log
                                        tempFile.close()
                                completedFiles(strKey) #Housekeeping to remove the file list after a successful compression backup
                                stat.load_app(strKey.split('.')[0]) #Reloads App after the compression is complete
                            else:
                                print '%s.7z failed' % strKey #Compression failed
                        else:
                            print "Cannot run compression as Application: %s is running" %(strKey.split('.')[0]) #If Application is running and bRunning is set to False
                        
                    else:#App is not running, so additional steps are not needed
                        if compressFiles(strKey,fileList.name)==0: #File list sent to 7z for compression
                            fileListLines=open('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey,'rb').readlines() #Open filelst to scan for .log file
                            for itemLines in fileListLines:
                                if itemLines.lower().find('log')<>-1 and bClear=="T": #Found .log file, and will clear it if bClear is equal to "T"
                                    tempFile=open(itemLines[1:-3],'wb')
                                    tempFile.close()
                            completedFiles(strKey) #Housekeeping to remove the file list after a successful compression backup
                        else:
                            print '%s.7z failed' % strKey #Compression failed 
                else:
                    Dbs_stat=stat.display_database(strKey) # Checking the status of the Database
                    print Dbs_stat
                    if Dbs_stat==2 and bRunning<>'F': #check to see if database is running and can be shutdown
                        if stat.unload_db(strKey.split('.')[0],strKey.split('.')[1])==0: #Shutting down database for backup
                            if compressFiles(strKey,fileList.name)==0: #Compressing files returns 0 is successful
                                completedFiles(strKey)#Housekeeping to remove the file list after a successful compression backup
                                stat.load_db(strKey.split('.')[0],strKey.split('.')[1])#Loading database again
                            else:
                                print '%s.7z failed' % strKey #Compression failed
                        else:
                            print "Cannot run compression as Database: %s is running" % (strKey) #Database is running and not allowed to be shutdown for backup
                        
                    else:
                        if compressFiles(strKey,fileList.name)==0: #Database is already shutdown, no additional checks needed
                            completedFiles(strKey)#Housekeeping to remove the file list after a successful compression backup
                        else:
                            print '%s.7z failed' % strKey#Compression failed
            else:#This section archives the prepended $ sign directory The folder exists under the app directory, but is not an Essbase app/database
                if compressFiles(strKey,fileList.name)==0:
                    print '%s.7z is complete' % strKey
                    listComplete.append('%s.7z' % strKey)
                    os.remove('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey)
                else:
                    print '%s.7z failed' % strKey
    else: #Essbase is not running. No restrictions on backup due to applcation/database status
        for strKey in listKeys:
            print strKey
            fileList=open('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey,'wb')
            for strPath in dictApps_Dbs[strKey]:
                print strPath
                fileList.write('"%s"\r\n' % strPath)
                fileList.flush()
            fileList.close()
            
            if compressFiles(strKey,fileList.name)==0:
                fileListLines=open('d:\\Hyperion_filelst\\filelist_%s.lst' % strKey,'rb').readlines()
                for itemLines in fileListLines:
                    if itemLines.lower().find('log')<>-1 and options.bClear=="T":
                        tempFile=open(itemLines[1:-3],'wb')
                        tempFile.close()
                completedFiles(strKey)
            else:
                print '%s.7z failed' % strKey

    fileList.close() #Close open files
    outputFile.close()
    stat.disconnect() #Disconnect from Essbase
    #Store all output 7z files
    sts=storeFiles(strDate[0],strDate[1],strDate[2])#Creates the storage 7z file using the format of YYYY_MM_DD.7z
    if sts==0:
        for item in listComplete:
            os.remove('%s%s' % ('d:\\Hyperion_files\\',item))#Housekeeping to remove individual compressed files, as they have been included in the stored 7z file
        os.remove('d:\\Hyperion_filelst\\all.log')#Housekeeping to remove the all.log after storage is complete
        
'''
To display PIDs for esssvr.exe process
>>> stat.app_process_id('testserver','hypadmin',None)
[4388, 3412, 3668, 3760, 596]

>>> stat.find_application_process_id('testserver',str(4388))
Application [TEST_FIN] started with process id [4388]

('TEST_FIN', '4388')
    
>>> pids=stat.app_process_id('testserver','hypadmin',None)
>>> for pid in pids:
... 	stat.find_application_process_id('testserver',str(pid))
... 
Application [TEST_FIN] started with process id [4388]

('TEST_FIN', '4388')
Application [TEST_STK] started with process id [3412]

('TEST_STK', '3412')
Application [TESTPlan] started with process id [3668]

('TESTPlan', '3668')
Application [TEST_TEST] started with process id [3760]

('TEST_TEST', '3760')
Application [TEST_ABC] started with process id [596]

('TEST_ABC', '596')
'''