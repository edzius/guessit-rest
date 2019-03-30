
import os
import json
import logging

OMDB_CACHE_INDEX = "/var/run/omdbref/fetch.index"
OMDB_CACHE_DIR = "/var/run/omdbref/fetch-cache"

omdb_index = None

def init():
    if os.path.exists(OMDB_CACHE_DIR):
        return
    os.makedirs(OMDB_CACHE_DIR)

def load():
    global omdb_index

    if omdb_index:
        return

    omdb_index = {}
    try:
        fp = open(OMDB_CACHE_INDEX)
    except:
        return

    for line in fp:
        line = line.strip()
        if not line:
            logging.warning("Empty omdb cache index line")
            continue
        mid, _, mname = line.partition('=')
        if not mid:
            logging.warning("Invalid omdb cache index line: %s", line)
            continue

        omdb_index[mname.strip()] = mid.strip()

    fp.close()

def get(name):
    global omdb_index

    load()

    name = name.strip()
    if name not in omdb_index:
        logging.debug("Cache get '%s' failed - not in index", name)
        return

    mid = omdb_index[name].strip()

    init()
    try:
        fp = open("%s/%s" % (OMDB_CACHE_DIR, mid,))
    except Exception as e:
        logging.error("Failed omdb cache get '%s' (%s): %s", name, mid, e)
        return
    data = json.load(fp)
    fp.close()
    return data

def set(data, name):
    global omdb_index

    if not data:
        return

    mid = data['imdb_id']
    mname = name or data['title']

    mid = mid.strip()
    mname = mname.strip()
    if mname in omdb_index:
        logging.debug("Cache set '%s' skipped - already in index", mname)
        return

    init()
    try:
        fp = open("%s/%s" % (OMDB_CACHE_DIR, mid,), "w")
    except Exception as e:
        logging.error("Failed omdb cache set '%s' (%s): %s", mname, mid, e)
        return

    json.dump(data, fp)
    fp.close()

    try:
        fp = open(OMDB_CACHE_INDEX, "a")
    except Exception as e:
        logging.error("Failed omdb cache index update '%s' (%s): %s", mname, mid, e)
        return

    fp.write("%s=%s\n" % (mid, mname,))
    fp.close()

    omdb_index[mname] = mid

def convert(data):
    if not data:
        return
    return json.loads(data)
