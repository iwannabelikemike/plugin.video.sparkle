# -*- coding: utf-8 -*-

import os
import json
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

from resources.lib.modules.log_utils import log

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

default_streaming_subreddits = [
    {'name': 'Soccer streams', 'url': 'RedditSoccerCity'},
    {'name': 'MMA Streams', 'url': 'MMAStreams'},
    {'name': 'NFL Streams', 'url': 'NFLStreams'},
    {'name': 'NBA Streams', 'url': 'nbastreams'},
    {'name': 'Cricket Streams', 'url': 'cricketstreams'},
    {'name': 'NCAA BBall Streams', 'url': 'ncaaBBallStreams'},
    {'name': 'CFB Streams', 'url': 'CFBStreams'},
    {'name': 'NHL Streams', 'url': 'NHLStreams'},
    {'name': 'Puck Streams', 'url': 'puckstreams'},
    {'name': 'MLB Streams', 'url': 'MLBStreams'},
    {'name': 'Tennis Streams', 'url': 'TennisStreams'},
    {'name': 'Boxing Streams', 'url': 'BoxingStreams'},
    {'name': 'Rugby Streams', 'url': 'RugbyStreams'},
    {'name': 'Motor Sports Streams', 'url': 'motorsportsstreams'},
    {'name': 'WWE Streams', 'url': 'WWEstreams'},
]

_dataPath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8')
_subreddits_file = os.path.join(_dataPath, 'subreddits.db')
_db_table = 'subreddits'

class StreamingSubreddits():

    def __init__(self):
        # Initialize the subreddits db file if doesn't exist
        if not os.path.exists(_subreddits_file):
            xbmcvfs.mkdir(_dataPath)
            self.conn = self.initialize_db()
        else:
            self.conn = database.connect(_subreddits_file)

    def initialize_db(self):
        conn = database.connect(_subreddits_file)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS subreddits;")
        cur.execute("CREATE TABLE IF NOT EXISTS {tbl} (""url TEXT, ""name TEXT, ""UNIQUE(url)"");".format(tbl=_db_table))
        for k in default_streaming_subreddits:
            cur.execute("INSERT INTO {tbl} VALUES ('{url}', '{name}')".format(
                tbl=_db_table, url=k['url'], name=k['name']))
        conn.commit()
        xbmcgui.Dialog().notification(
            heading="DB Initialized",
            message="Initialized ",
            icon=xbmcgui.NOTIFICATION_INFO,
            time=3000,
            sound=False)
        return conn

    def get_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM {}".format(_db_table))
        items = cur.fetchall()
        return [(i[0].encode('utf-8'), i[1].encode('utf-8')) for i in items]

    def add_entry(self, url, name):
        cur = self.conn.cursor()
        try:
            statement = "INSERT INTO {} (url, name) VALUES ('{}', '{}')".format(_db_table, url, name)
            log(statement)
            cur.execute(statement)
            self.conn.commit()
        except:
            xbmcgui.Dialog().notification(
                heading="Add entry",
                message="Couldn't add entry ({}, {}) for some reason".format(url, name),
                icon=xbmcgui.NOTIFICATION_INFO,
                time=3000,
                sound=False)
            raise

        xbmcgui.Dialog().notification(
            heading="Add entry",
            message="{} added".format(url),
            icon=xbmcgui.NOTIFICATION_INFO,
            time=3000,
            sound=False)

    def delete_entry(self, url):
        cur = self.conn.cursor()
        try:
            statement = "DELETE FROM {} WHERE url = '{}'".format(_db_table, url)
            log(statement)
            cur.execute(statement)
            self.conn.commit()
        except:
            xbmcgui.Dialog().notification(
                heading="Delete",
                message="Couldn't delete {} for some reason".format(url),
                icon=xbmcgui.NOTIFICATION_INFO,
                time=3000,
                sound=False)
            raise

        xbmcgui.Dialog().notification(
            heading="Delete",
            message="{} deleted".format(url),
            icon=xbmcgui.NOTIFICATION_INFO,
            time=3000,
            sound=False)

    def reset_entries(self):
        self.initialize_db()

    def __del__(self):
        self.conn.close()
