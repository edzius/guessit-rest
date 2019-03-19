
import omdb
from omdbref import API_KEY
from omdbref import omdbcache
from omdbref import omdblog

omdb.set_default('apikey', API_KEY)

def verify(data):
    if not data:
        return False

    if 'Response' in data and data['Response'] != "True":
        return False

    if 'response' in data and data['response'] != "True":
        return False

    return True

def update(data, name):
    if not data or len(data) == 0:
        omdblog.write("No data provided for: %s", name or "None")
        return

    if 'title' not in data:
        omdblog.write("No title found for: %s", name or "None")
        return
    title = data['title']

    odata = None
    try:
        odata = omdbcache.get(title)
        if not odata:
            odata = omdb.get(title=title)
            if verify(odata):
                omdbcache.set(odata, title)
            else:
                omdblog.write("OMDB fetch responded: %s", odata)
    except Exception as e:
        omdblog.write("OMDB fetch failed: %s" % e)

    data["ext"] = odata
    return data
