
OMDB_LOG_FILE = "omdb.log"

logfp = None

def init():
    return open(OMDB_LOG_FILE, "a")

def write(fmt, *args):
    global logfp
    if not logfp:
        logfp = init()

    line = fmt % args
    logfp.write("%s\n" % line)
    logfp.flush()

