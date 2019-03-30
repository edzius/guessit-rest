
import os
import logging
import omdb
from omdbref import omdbcache

def read_key_config(file_name):
    try:
        fh = open(file_name, 'r')
    except Exception as e:
        logging.debug("Cannot read key file '%s': %s", file_name, e)
        return ''

    key = fh.readline() or ''
    fh.close()
    return key.strip()

def read_key_env(env_name):
    try:
        return os.environ[env_name]
    except Exception as e:
        logging.debug("Cannot get key env '%s': %s", env_name, e)
        return ''

key = read_key_env('OMDB_KEY') or read_key_config('~/.config/guessit/omdb-key') or read_key_config('/etc/guessit/omdb-key')
if not key:
    logging.error("No OMDB key configured")
omdb.set_default('apikey', key or '')

def verify(data):
    if not data:
        return False

    if 'Response' in data and data['Response'] != "True":
        return False

    if 'response' in data and data['response'] != "True":
        return False

    return True

def receive(title, kind, season=None, episode=None):
    name = ' '.join([str(title),
                     str('S%s' % season) if season else '',
                     str('E%s' % episode) if episode else '']).strip()

    try:
        data = omdbcache.get(name)
        if data:
            return data

        if not key:
            logging.info("OMDB fetch '%s' skipped; KEY not set", name)
            return data

        logging.info("OMDB fetch '%s' new data", name)
        data = omdb.get(title=title,media_type=kind,season=season,episode=episode)

        if verify(data):
            omdbcache.set(data, name)
            return data

        logging.warning("OMDB fetch '%s' responded: %s", name, data)
    except Exception as e:
        logging.warning("OMDB fetch '%s' failed: %s", name, e)
