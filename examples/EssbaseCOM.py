import Essbase
import sys

class EssbaseMaxL():
    _public_methods_ = [ 'connect', 'do', 'pop_msg', 'fetch_desc', 'fetch_row', 'disconnect', 'msgs', 'execute' ]
    _public_attrs_ = [ 'numFlds', 'sts' ]
    _readonly_attrs_ = [ 'numFlds', 'sts' ]
    _reg_progid_ = "Essbase.MaxL"
    _reg_verprogid_ = _reg_progid_ + ".657"

    # NEVER copy the following ID
    # Use "print pythoncom.CreateGuid()" to make a new one.
    _reg_clsid_ = "{473C368D-E49B-4A79-ABCB-D2E9DAB2F360}"
    
    def __init__(self):
        self.esb = Essbase.Essbase()
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError,'no attribute named %s' % name

    def connect(self, user, password, host='localhost'):
        retval = self.esb.connect(user, password, host)
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def do(self, statement):
        retval = self.esb.do(statement)
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def pop_msg(self):
        retval = self.esb.pop_msg()
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def fetch_desc(self):
        retval = self.esb.fetch_desc()
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def fetch_row(self):
        retval = self.esb.fetch_row()
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def disconnect(self):
        retval = self.esb.disconnect()
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def msgs(self, output=sys.stdout):
        retval = self.esb.msgs(output)
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

    def execute(self, stmt, output=sys.stdout):
        retval = self.esb.execute(stmt, output)
        self.numFlds = self.esb.numFlds
        self.sts = self.esb.sts
        return retval

# Add code so that when this script is run by
# Python.exe, it self-registers.
if __name__=='__main__':
    print "Registering COM server..."
    import win32com.server.register
    win32com.server.register.UseCommandLine(EssbaseMaxL)
