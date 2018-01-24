from ctypes import *
from ctypes.util import find_library
import time
import sys
import platform
import os
import re

BIT64 = platform.architecture()[0] == '64bit'

# Essbase constants
ESS_BYTES_PER_CHARACTER     = 4
ESS_BYTES_FOR_TRAILING_NULL = 5
ESS_TRUE                    = 1

# Change this to to True for Unicode enablement
ESS_UTF                     = False

#MaxL constants
MAXL_OPMODE_DEFAULT         = 0
MAXL_OPMODE_UTF             = 2
MAXL_MSGTEXT_LEN_NATIVE     = 256
MAXL_MSGTEXT_LEN            = ((MAXL_MSGTEXT_LEN_NATIVE * ESS_BYTES_PER_CHARACTER) + ESS_BYTES_FOR_TRAILING_NULL)
MAXL_COLUMN_NAME_LEN_NATIVE = 64
MAXL_COLUMN_NAME_LEN        = ((MAXL_COLUMN_NAME_LEN_NATIVE * ESS_BYTES_PER_CHARACTER) + ESS_BYTES_FOR_TRAILING_NULL)
MAXL_MSGNO_COL_PREP_NUM     = 1241045
# has to be set later depending on the version of the DLL, this is the standard value for version 11.1.2.4
MAXL_MDXCELLSTRSZ           = 1024 + 3

# Return codes as defined in maxldefs.h
MAXL_MSGLVL_SUCCESS     = 0
MAXL_MSGLVL_WARNING     = 1
MAXL_MSGLVL_ERROR       = 2
MAXL_MSGLVL_SESSION     = 5
MAXL_MSGLVL_FATAL       = 6
MAXL_MSGLVL_END_OF_DATA = 108

# MaxL's internal data types (maxldefs.h)
MAXL_DTINT_BOOL     = 1
MAXL_DTINT_NUMBER   = 2
MAXL_DTINT_CHAR     = 3
MAXL_DTINT_DOUBLE   = 4
MAXL_DTINT_ULONG64  = 5 # added for 11.1.2.2+

# External data types supported by MaxL (maxldefs.h)
MAXL_DTEXT_UCHAR    = 2
MAXL_DTEXT_DOUBLE   = 10
MAXL_DTEXT_STRING   = 11
MAXL_DTEXT_ULONG64  = 12 # added for 11.1.2.2+

# MDX column types supported by MaxL (maxldefs.h)
MAXL_MDXINTTYPE     = 0
MAXL_MDXLONGTYPE    = 1
MAXL_MDXULONGTYPE   = 2
MAXL_MDXSHORTTYPE   = 3
MAXL_MDXUSHORTTYPE  = 4
MAXL_MDXFLOATTYPE   = 5
MAXL_MDXSTRTYPE     = 6
MAXL_MDXMEMTYPE     = 7
MAXL_MDXDATASTRTYPE = 8

#Other constants
MAX_REC = 1     # we are going to retrieve one record at a time
MAX_COL = 1024  # maximum column size

ESS_PVOID_T = c_void_p
ESS_PPVOID_T = POINTER(ESS_PVOID_T)

def getFileVerInfo(FileName):
    """
    returns the file information from EXE and DLL.
    stripped version from https://www.python-forum.de/viewtopic.php?t=2306
    """
    FileHandle = open( FileName, "rb" )
    RAWdata = FileHandle.read().replace(b"\x00",b"")
    FileHandle.close()

    Info = re.findall(b"FileVersion"+b"(.+?)\x01", RAWdata )
    if Info == []:
        return None
    else:
        return Info[0][:-2]

class maxl_instinit_t(Structure):
    _fields_ = [('MsgText', (c_char * MAXL_MSGTEXT_LEN)),
                ('MsgTextFill', (c_char * 3)),
                ('bUTFInput', c_ubyte),
                ('bTempFillerArray', (c_ubyte * 7)),
                ('CtxListLen', c_ushort)]

if BIT64:
    class maxl_ssninit_t(Structure):
        _fields_ = [('MsgText', (c_char * MAXL_MSGTEXT_LEN)),
                    ('MsgTextFill', (c_char * 3)),
                    ('MsgLevel', c_ulong),
                    ('ulTempFiller1', c_ulong),
                    ('MsgNumber', c_long),
                    ('ulTempFiller2', c_ulong),
                    ('ExecElapsedTime', c_ulong),
                    ('ulTempFiller3', c_ulong),
                    ('ExecArity', c_ulong),
                    ('ulTempFiller4', c_ulong),
                    ('RowCount', c_ulong),
                    ('ulTempFiller5', c_ulong),
                    ('Card', c_ulong),
                    ('ulTempFiller6', c_ulong),
                    ('bMdxQuery', c_ulong),
                    ('ulTempFiller7', c_ulong),
                    ('pNewPassword', c_char_p),
                    ('pReserved1', c_void_p),
                    ('pReserved2', c_void_p),
                    ('pReserved3', c_void_p),
                    ('pReserved4', c_void_p),
                    ('ExecVerb', c_ulong),
                    ('ulTempFiller8', c_ulong)]
else:
    class maxl_ssninit_t(Structure):
        _fields_ = [('MsgText', (c_char * MAXL_MSGTEXT_LEN)),
                    ('MsgTextFill', (c_char * 3)),
                    ('MsgLevel', c_ulong),
                    ('MsgNumber', c_long),
                    ('ExecElapsedTime', c_ulong),
                    ('ExecArity', c_ulong),
                    ('RowCount', c_ulong),
                    ('Card', c_ulong),
                    ('bMdxQuery', c_ulong),
                    ('pNewPassword', c_char_p),
                    ('pReserved1', c_void_p),
                    ('pReserved2', c_void_p),
                    ('pReserved3', c_void_p),
                    ('pReserved4', c_void_p),
                    ('ExecVerb', c_ulong)]

if BIT64:
    class maxl_column_descr_t(Structure):
        _fields_ = [('Name', (c_char * MAXL_COLUMN_NAME_LEN)),
                    ('NameFill', (c_char * 3)),
                    ('IntTyp', c_ulong),
                    ('ulTempFiller1', c_ulong),
                    ('IntLen', c_long),
                    ('ulTempFiller2', c_ulong),
                    ('IntRealLen', c_ulong),
                    ('ulTempFiller3', c_ulong)]
else:
    class maxl_column_descr_t(Structure):
        _fields_ = [('Name', (c_char * MAXL_COLUMN_NAME_LEN)),
                    ('NameFill', (c_char * 3)),
                    ('IntTyp', c_ulong),
                    ('IntLen', c_long),
                    ('IntRealLen', c_ulong)]

MAXL_MDXCOLUMNTYPE_T = c_ulong
class maxl_mdxoutputheader_t(Structure):
    _fields_ = [('Type', MAXL_MDXCOLUMNTYPE_T),
                ('sName', (c_char * MAXL_MDXCELLSTRSZ))]


class Essbase:
    
    def __init__(self):
        self.user = None
        self.sid = None
        self.ssnInit = None
        self.numRows = None
        self.numFlds = None
        self.sts = None
        self.bMdxQuery = None

        # Check for environment variables needed for essbase
        try:
            os.environ["ESSBASEPATH"]
            os.environ["PATH"]
        except KeyError as e:
            print ("environment variable {VAR} not set".format(VAR=e))
            raise SystemExit
        
        # Initialize MaxL API
        inst = maxl_instinit_t()
        
        # Try to find and load the DLL
        __maxldll = find_library('essmaxlu')
        if __maxldll:
            print ("Using Maxl DLL in {DLLpath}".format(DLLpath = __maxldll))
            if b"11.1.2.4" in (getFileVerInfo(__maxldll)):
                MAXL_MDXCELLSTRSZ           = 1024 + 3
            else:
                MAXL_MDXCELLSTRSZ           = 1024
            self.maxl = cdll.LoadLibrary(__maxldll)
        else:
            print ("maxl DLL not found")
            raise SystemExit

        if ESS_UTF:
            inst.bUTFInput = ESS_TRUE

        sts = self.maxl.MaxLInit(byref(inst))
        Essbase.isInitialized = (sts == MAXL_MSGLVL_SUCCESS)
        
    def __del__(self):
        if Essbase.isInitialized:
            # Terminate MaxL API
            sts = self.maxl.MaxLTerm()
            Essbase.isInitialized = False

    """---------------------------- connect -----------------------------------
    
    Creates new Essbase Session.
    
    Arguments:
      User name.  Required.  Character string containing valid Essbase
                             user name in whose security domain the new
                             session is to be established.
      Password.   Required.  Password for the user.
      Host name.  Optional.  The computer name hosting the Essbase instance
                             of interest.
    """
    def connect(self, user, password, host='localhost'):
        self.sid = c_ushort(0)
        self.ssnInit = maxl_ssninit_t()
        self.sts = self.maxl.MaxLSessionCreate(c_char_p(host.encode('utf-8')), c_char_p(user.encode('utf-8')), c_char_p(password.encode('utf-8')), byref(self.ssnInit), byref(self.sid))
        self.user = user
        self.numFlds = 0
        self.bMdxQuery = 0

    """-------------------------------- do ------------------------------------
    
    Performs a MaxL statement.
    
    Arguments:
      Statement. Required. A string containing a MaxL statement to be
                           passed to the server.
    
    Returns (and sets Essbase{STATUS} to):
    
      $MAXL_STATUS {NOERR} if execution was successful.  There are likely
         to be informational and feedback massages on the message stack,
         which may be obtained with the pop_msg() method below.
    
      $MAXL_STATUS {ERROR} if there was a user error.  The numbers of
         the encountered errors, their levels and texts may be obtained
         with the pop_msg method below.  Note, that there's likely to
         be informational messages on the message stack even in if
         execution was successful.  These also may be obtained via the
         pop_msg call below.
    """
    def do(self, statement):
        if not (self.sid and self.ssnInit):
            return MAXL_MSGLVL_SESSION

        # execute the statement command
        if ESS_UTF:
            self.sts = self.maxl.MaxLExec(self.sid, c_char_p(statement.encode('utf-8')), c_ulong(MAXL_OPMODE_UTF))
        else:
            self.sts = self.maxl.MaxLExec(self.sid, c_char_p(statement.encode('utf-8')), c_ulong(MAXL_OPMODE_DEFAULT))

        if self.is_mdx():
            numFlds = c_long(0)
            numRows = c_long(0)
            self.sts = self.maxl.MaxlMDXOutputSize(self.sid, byref(numFlds), byref(numRows))
            
            if self.sts > MAXL_MSGLVL_ERROR:
                self.numFlds = None
                self.numRows = None
            else:
                self.numFlds = int(numFlds.value)
                self.numRows = int(numRows.value)
        else:
            if self.sts > MAXL_MSGLVL_ERROR:
                self.numFlds = None
            else:
                self.numFlds = self.ssnInit.ExecArity

        return self.sts

    """---------------------------- pop_msg -----------------------------------
    
    Pops next Essbase or MaxL status message from MaxL message stack.
    
    Each invocation of the "do" method above results in a stack of status
    messages.  This stack is unwound by repeatedly calling this function
    until it returns nothing.  It's okay for a program to ignore the
    message stack, or only unwind it partially.  The next call to "do" will
    clear left-over messages.
    
    There is likely to be a number of messages on the stack even after a
    successful execution.  In most cases, a program will only need
    to know if the execution of the last "do" was successful, which is
    indicated by the return value from "do".
    
    When the message stack is empty the return list elements are undefined
    and Essbase{STATUS} is set to $MAXL_STATUS{END_OF_DATA}.
    
    Arguments: None
    
    Returns: List of form:
      (<message_number>, <message_level>, <message_text>)
    """
    def pop_msg(self):
        if not (self.sid and self.ssnInit):
            return None, None, None

        msgno = msglevel = arity = 0
        done = False
        getAnotherMessage = True

        while getAnotherMessage:
            msgstr = ''
            if self.sts <= MAXL_MSGLVL_ERROR:
                msgno, msglevel, msgstr, arity = self.ssnInit.MsgNumber, self.ssnInit.MsgLevel, self.ssnInit.MsgText, self.ssnInit.ExecArity
                if not (not arity and msgno == MAXL_MSGNO_COL_PREP_NUM):
                    getAnotherMessage = False
                else:
                    getAnotherMessage = True
            elif self.sts == MAXL_MSGLVL_END_OF_DATA:
                done = True
                getAnotherMessage = False

            if not done:
                self.sts = self.maxl.MaxLMessageFetch(self.sid)
                if getAnotherMessage:
                    msgno = msglevel = arity = 0

        if self.sts > MAXL_MSGLVL_ERROR and self.sts != MAXL_MSGLVL_END_OF_DATA:
            msgno, msglevel, msgstr = None, None, None

        return msgno, msglevel, msgstr

    """------------------------- fetch_desc ------------------------------
    
    Returns reference to list of column names in the output table
    and a reference to the list of column types in the output table.
    """
    def fetch_desc(self):
        col_names = []
        col_types = []

        if not self.sid:
            return MAXL_MSGLVL_SESSION

        if not self.numFlds:
            return tuple(col_names), tuple(col_types)

        if self.is_mdx():
            pHeader_t = POINTER(maxl_mdxoutputheader_t)
            pHeader = pHeader_t()
            self.sts = self.maxl.MaxlMDXOutputDescribe(self.sid, byref(pHeader))
            if self.sts < MAXL_MSGLVL_ERROR:
                for index in range(self.numFlds):
                    col_names.append(pHeader[index].sName)
                    col_types.append(pHeader[index].Type)
        else:
            col_array = maxl_column_descr_t * self.numFlds
            cols = col_array()
            self.sts = self.maxl.MaxLOutputDescribe(self.sid, c_ulong(1), c_ulong(self.numFlds), byref(cols))
            if self.sts < MAXL_MSGLVL_ERROR:
                for index in range(self.numFlds):
                    col_names.append(cols[index].Name)
                    col_types.append(cols[index].IntTyp)

        return tuple(col_names), tuple(col_types)

    """------------------------- fetch_row ------------------------------
    
    Returns a reference to a row of query results in output table as a
    list and a reference to the data types of the query result values
    as a list.
    Essbase->{STATUS} is set to either $MAXL_STATUS{NOERR}, on
    success, or $MAXL_STATUS{END_OF_DATA}, if there were no rows to
    fetch, or $MAXL_STATUS{ERROR} if a user error has occured.
    
    A row of record is defined as
       { val[0], val[1], ... , val[NUM_OF_FIELDS-1] } }
    Row numbers are counted cardinally from 0:
    """
    def fetch_row(self):
        row = []
        
        if not (self.sid and self.ssnInit):
            return MAXL_MSGLVL_SESSION

        if not self.numFlds:
            return row

        if self.bMdxQuery:
            self.sts, row = self._MaxlMDXOutputNextRecord(self.sid, self.numFlds)
        else:
            self.sts, row = self._MaxlOutputNextRecord(self.sid, self.ssnInit, self.numFlds)

        if self.sts == MAXL_MSGLVL_END_OF_DATA:
            self.sts = MAXL_MSGLVL_SUCCESS

        return row

    """----------------------- _MaxlOutputNextRecord --------------------"""
    def _MaxlOutputNextRecord(self, sid, ssnInit, numFlds):
        row = []
        pDescr = maxl_column_descr_t()

        descr_array = maxl_column_descr_t * numFlds
        pOutputDescrs = descr_array()

        col_t = c_char * (MAX_COL + 1)

        class output_buffer(Union):
            _fields_ = [('pdVal', c_double * MAX_REC),
                        ('pbVal', c_ubyte * MAX_REC),
                        ('pszVal', col_t * MAX_REC),
                        ('puVal', c_ulonglong * MAX_REC)]

        sts = self.maxl.MaxLOutputDescribe(sid, c_ulong(1), c_ulong(numFlds), byref(pOutputDescrs))

        if sts < MAXL_MSGLVL_ERROR:
            buffer_array = output_buffer * numFlds
            pOutputArray = buffer_array()

            # memset(pOutputArray, 0, sizeof(pOutputArray))
            ppOutputArray = (c_char * sizeof(pOutputArray)).from_address(addressof(pOutputArray))
            ppOutputArray.value = b'\0' * sizeof(pOutputArray)

            for index in range(numFlds):
                pBuffer = pOutputArray[index]
                pDescr = pOutputDescrs[index]

                if pDescr.IntTyp in (MAXL_DTINT_DOUBLE, MAXL_DTINT_NUMBER):
                    pInBuff = pBuffer.pdVal
                    Type = MAXL_DTEXT_DOUBLE
                    Size = 0
                elif pDescr.IntTyp == MAXL_DTINT_BOOL:
                    pInBuff = pBuffer.pbVal
                    Type = MAXL_DTEXT_UCHAR
                    Size = 0
                elif pDescr.IntTyp == MAXL_DTINT_CHAR:
                    pInBuff = pBuffer.pszVal
                    Type = MAXL_DTEXT_STRING
                    Size = MAX_COL+1
                elif pDescr.IntTyp == MAXL_DTINT_ULONG64:
                    pInBuff = pBuffer.puVal
                    Type = MAXL_DTEXT_ULONG64
                    Size = 0

                sts = self.maxl.MaxLColumnDefine(sid, c_ulong(index + 1), pInBuff, c_ushort(Size), c_ulong(Type), c_ushort(MAX_REC), None, None)
                if sts >= MAXL_MSGLVL_ERROR:
                    pOutputDescrs = pOutputArray = None
                    return sts, None

            sts = self.maxl.MaxLOutputFetch(sid, c_ulong(MAXL_OPMODE_DEFAULT))
            if sts == MAXL_MSGLVL_ERROR or sts == MAXL_MSGLVL_END_OF_DATA:
                return sts, None
            elif sts > MAXL_MSGLVL_ERROR:
                pOutputDescrs = pOutputArray = None
                return sts, None

            for index in range(numFlds):
                pDescr = pOutputDescrs[index]
                pBuffer = pOutputArray[index]
                if pDescr.IntTyp in (MAXL_DTINT_DOUBLE, MAXL_DTINT_NUMBER):
                    row.append(pBuffer.pdVal[0])
                elif pDescr.IntTyp == MAXL_DTINT_BOOL:
                    row.append(pBuffer.pbVal[0])
                elif pDescr.IntTyp == MAXL_DTINT_CHAR:
                    row.append(pBuffer.pszVal[0].value)
                elif pDescr.IntTyp == MAXL_DTINT_ULONG64:
                    row.append(pBuffer.puVal[0])

        pOutputDescrs = None
        pOutputArray = None
        return sts, row

    """-------------------- _MaxlMDXOutputNextRecord --------------------
    
    Description
      Returns pOutput->ulCurRow'th row of output data.
    
    Parameters
      SessionId- in    - MaxL Session id.
      ppRecord - out   - Pointer to the buffer which receives the record
                          values.
    
    Returns
      MAXL_NOERR, MAXL_END_OF_DATA, MAXL_ERROR.
    """
    def _MaxlMDXOutputNextRecord(self, sid, numFlds):
        row = []
        pHeader_t = POINTER(maxl_mdxoutputheader_t)
        pHeader = pHeader_t()

        #ESS_PPVOID_T ppRecord;
        #ppRecord = malloc(sizeof(ESS_PVOID_T) * ulNumCols)
        ppRecordAry = ESS_PVOID_T * numFlds
        ppRecord = ppRecordAry()

        sts = self.maxl.MaxlMDXOutputNextRecord(sid, ppRecord)
        if sts == MAXL_MSGLVL_SUCCESS:
            sts = self.maxl.MaxlMDXOutputDescribe(sid, byref(pHeader))
            if sts == MAXL_MSGLVL_SUCCESS:
                for index in range(numFlds):
                    fldType = pHeader[index].Type
                    if fldType in (MAXL_MDXINTTYPE, MAXL_MDXLONGTYPE):
                        row.append(cast(ppRecord[index], POINTER(c_long))[0])
                    elif fldType == MAXL_MDXULONGTYPE:
                        row.append(cast(ppRecord[index], POINTER(c_ulong))[0])
                    elif fldType == MAXL_MDXSHORTTYPE:
                        row.append(cast(ppRecord[index], POINTER(c_short))[0])
                    elif fldType == MAXL_MDXUSHORTTYPE:
                        row.append(cast(ppRecord[index], POINTER(c_ushort))[0])
                    elif fldType in (MAXL_MDXFLOATTYPE, MAXL_MDXMEMTYPE):
                        row.append(cast(ppRecord[index], POINTER(c_double))[0])
                    elif fldType in (MAXL_MDXDATASTRTYPE, MAXL_MDXSTRTYPE):
                        row.append(cast(ppRecord[index], POINTER(c_char_p))[0])
                    else:
                        row.append("")

        return sts, row

    """----------------------------- is_mdx -------------------------------
    
    This function can be called after a call to do() in case different
    output processing is desired for mdx query output than from
    MaxL command output
    """
    def is_mdx(self):
        if not (self.sid and self.ssnInit):
            return None

        return self.ssnInit.bMdxQuery

    """----------------------------- disconnect -------------------------------
    
    Terminates a MaxL session and the associated Essbase session.
    """
    def disconnect(self):
        if not self.sid:
            return MAXL_MSGLVL_SESSION

        self.sts = self.maxl.MaxLSessionDestroy(self.sid)

        if self.sts < MAXL_MSGLVL_ERROR:
            self.user = None
            self.sid = None
            self.ssnInit = None
            self.numFlds = None
            self.sts = None

        return self.sts

    """-------------------------------- rows ----------------------------------
    
    Generator that loops through output returned by Essbase 
    """
    def rows(self, value=None):
        if not self.numFlds:
            raise StopIteration
        else:
            try:
                row = self.fetch_row()
                while row:
                    value = (yield row)
                    row = self.fetch_row()
            except GeneratorExit:
                raise
            except Exception as e:
                value = e
                raise

    """--------------------------------- tdf ---------------------------------
    
    Returns a result set in the form of a tab-delimited file.
    """
    def tdf(self):
        # setup the header
        name, dt = self.fetch_desc()
        tbl = "\t".join([x.decode() for x in name]) + "\n"
        line = ['-' * len(column) for column in name]
        tbl = tbl + "\t".join(line) + "\n"

        # now populate the tab-delimited file with data
        for row in self.rows():
            record = []
            idx = 0
            for column in row:
                if dt[idx] == MAXL_DTINT_BOOL:
                    if column == 0:
                        record.append('FALSE')
                    else:
                        record.append('TRUE')
                else:
                    if type(column) == bytes:
                        record.append(column.decode())
                    else:
                        record.append(str(column))
                idx += 1
            tbl = tbl + "\t".join(record) + "\n"

        tbl = tbl + "\n"

        return tbl

    """-------------------------------- msgs ----------------------------------
    
    Returns a message list that resulted from executing a MaxL statement.
    """
    def msgs(self, output=sys.stdout):

        msgno, level, msg = self.pop_msg()

        while msgno:
            # Decode message level
            if level == MAXL_MSGLVL_SUCCESS:
                msglvl = "OK/INFO"
            elif level == MAXL_MSGLVL_WARNING:
                msglvl = "WARNING"
            elif level == MAXL_MSGLVL_ERROR:
                msglvl = "ERROR"
            elif level == MAXL_MSGLVL_FATAL:
                msglvl = "FATAL"
            else:
                msglvl = str(level)
            print ("%8s - %7d - %s." % (msglvl, msgno, msg.decode()))
            msgno, level, msg = self.pop_msg()

        print ('')

    """------------------------------- execute -------------------------------
    
    Execute a MaxL statement and print resulting output.
    """
    def execute(self, stmt, output=sys.stdout, timefmt=None):
        # format MaxL statement for output
        stmt = stmt.replace("\t", "")
        out = stmt.split("\n")
        for i in range(1, len(out)):
            out[i] = "%4d> %s" % (i, out[i])
        if timefmt:
            timestamp = time.strftime(timefmt)
        else:
            timestamp = time.asctime()
        
        print (timestamp)
        print ("MAXL> %s;\n" % "\n".join(out))

        # execute MaxL statement
        sts = self.do(stmt)

        # exit if the execution failed
        if sts:
            # dump status messages
            self.msgs(output)

            print ("Execution of [%s] failed with status %d" % (stmt, sts))
        elif self.numFlds:
            print (self.tdf())

        # dump status messages
        self.msgs(output)

        return sts

