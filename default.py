from __future__ import unicode_literals

import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import xbmc
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.modules.addon import Addon
from resources.lib.modules import routing
from resources.lib.modules.log_utils import log
from resources.lib.modules.subreddit_lists import streaming_subreddits

addon = Addon('plugin.video.sparkle', sys.argv)
addon_handle = int(sys.argv[1])

plugin = routing.Plugin()

AddonPath = addon.get_path()
IconPath = os.path.join(AddonPath , "resources/media/")
fanart = os.path.join(AddonPath + "/fanart.jpg")

# Update path so that praw doesnt complain
sys.path.append(os.path.join(AddonPath, 'resources/lib/modules'))
from resources.lib.modules.subreddits import SubRedditEvents

AS_LAUNCH_LINK = 'XBMC.RunPlugin(plugin://program.plexus/?mode=1&url={url}&name={name})'

def icon_path(filename):
    if 'http://' in filename:
        return filename
    return os.path.join(IconPath, filename)

@plugin.route('/')
def index():
    for sr in streaming_subreddits:
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(show_subreddit, sr['url']),
            ListItem(sr['name']), True)
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(all),
        ListItem('All Currently Playing'), True)
    endOfDirectory(plugin.handle)

@plugin.route('/subreddit/<subreddit_id>')
def show_subreddit(subreddit_id):
    sr = SubRedditEvents()
    for s in sr.get_events(subreddit_id):
        # Get the number of acestreams available for this event
        # Don't include it if there arent any available
        events = sr.get_event_links(s['submission_id'])
        if events and len(events) > 0:
            title = "{} ({} Streams)".format(s['title'], len(events))
            addDirectoryItem(
                plugin.handle,
                plugin.url_for(show_event, s['submission_id']),
                ListItem(title), True)
    endOfDirectory(plugin.handle)

@plugin.route('/event/<submission_id>')
def show_event(submission_id):
    sr = SubRedditEvents()
    events = sr.get_event_links(submission_id)
    for score, quality, acelink in events:
        url = plugin.url_for(play, stream_url=acelink)
        addDirectoryItem(
            plugin.handle,
            url,
            ListItem("{} ({} ups) {}".format(quality, score, acelink)), True)
    endOfDirectory(plugin.handle)

@plugin.route('/play')
def play():
    stream_url = plugin.args['stream_url'][0]
    log("Playing {}".format(stream_url))
    try:
        xbmc.executebuiltin(AS_LAUNCH_LINK.format(url=stream_url, name='sparkle'))
    except Exception as inst:
        log(inst)

@plugin.route('/all')
def all():
    sre = SubRedditEvents()
    for sr in streaming_subreddits:
        for s in sre.get_events(sr['url']):
            # Get the number of acestreams available for this event
            # Don't include it if there arent any available
            events = sre.get_event_links(s['submission_id'])
            if events and len(events) > 0:
                title = "[{}] {} ({} Streams)".format(sr['name'], s['title'], len(events))
                addDirectoryItem(
                    plugin.handle,
                    plugin.url_for(show_event, s['submission_id']),
                    ListItem(title), True)
    endOfDirectory(plugin.handle)

if __name__ == '__main__':
    plugin.run()
