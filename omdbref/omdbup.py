
import omdb
from omdbref import omdbcache
from omdbref import omdblog

OMDB_KEY = '/etc/omdb/key'

def read_key_config():
    try:
        fh = open(OMDB_KEY, 'r')
    except:
        return ''

    key = fh.readline() or ''
    fh.close()
    return key.strip()

omdb.set_default('apikey', read_key_config())

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
    kind = None
    season = None
    episode = None
    if 'type' in data:
        kind = data['type']
    if 'season' in data:
        season = data['season']
    if 'episode' in data:
        episode = data['episode']

    name = ' '.join([str(title),
                     str(kind) if kind else '',
                     str('S%s' % season) if season else '',
                     str('E%s' % episode) if episode else ''])

    odata = None
    sdata = None
    try:
        odata = omdbcache.get(name)
        if not odata:
            omdblog.write("OMDB fetch new '%s'", name)
            if kind == 'movie':
                odata = omdb.get(title=title,media_type='movie')
            elif kind == 'series' or kind == 'episode':
                odata = omdb.get(title=title,media_type='series')
            else:
                odata = omdb.get(title=title)

            if not verify(odata):
                omdblog.write("OMDB fetch '%s' responded: %s", title, odata)
                return

            if kind == 'episode' and episode:
                sdata = omdb.get(title=title,season=season,episode=episode)
                if not verify(sdata):
                    omdblog.write("OMDB fetch specific '%s' responded: %s", name, sdata)
                else:
                    odata['specific'] = sdata

            omdbcache.set(odata, name)
    except Exception as e:
        omdblog.write("OMDB fetch failed: %s", e)

    data["ext"] = odata
    return data
