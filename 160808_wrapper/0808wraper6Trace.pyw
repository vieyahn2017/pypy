#only linux

import sys,os,linecache

def trace(f):
    def globaltrace(frame,wht,arg):
        if why == "call":return localtrace
        return None
    
    def localtrace(frame,wht,arg):
        if why == "line":
            # record the file name and line number of every trace
            filename=frame.f_code.co_filename
            lineno=frame.f_lineno
            bname=os.path.basename(filename)
            print "{}({}): {}".format(
                bname,
                lineno,
                linecache.getline(filename, lineno).strip('\r\n')),
        return localtrace

    def _f(*args,**kwds):
        sys.settrace(globaltrace)
        result=f(*args,**kwds)
        sys.settrace(None)
        return result
    return _f

@trace
def test():
    print 1
    print 22
    print 333

#  only  linux???
