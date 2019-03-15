from __future__ import unicode_literals

import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import xbmc, xbmcgui
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.modules.addon import Addon
from resources.lib.modules import routing
from resources.lib.modules.log_utils import log
from resources.lib.modules.subreddit_lists import StreamingSubreddits

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
    ss = StreamingSubreddits()
    for (url, name) in ss.get_all():
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(show_subreddit, url),
            ListItem(name), True)
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(all),
        ListItem('All Currently Playing'), True)
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(settings),
        ListItem('Subreddit Settings'), True)
    endOfDirectory(plugin.handle)

@plugin.route('/settings')
def settings():
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(add_entry_dialog),
        ListItem('Add Subreddit Entry'), True)
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(delete_entry_dialog),
        ListItem('Delete Subreddit Entry'), True)
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(reset_entries),
        ListItem('Reset subreddit entries to defaults'), True)
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
            ListItem("{} ({} upvotes)".format(quality, score)), True)
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
    ss = StreamingSubreddits()
    for (url, name) in ss.get_all():
        for s in sre.get_events(url):
            # Get the number of acestreams available for this event
            # Don't include it if there arent any available
            events = sre.get_event_links(s['submission_id'])
            if events and len(events) > 0:
                title = "[{}] {} ({} Streams)".format(name, s['title'], len(events))
                addDirectoryItem(
                    plugin.handle,
                    plugin.url_for(show_event, s['submission_id']),
                    ListItem(title), True)
    endOfDirectory(plugin.handle)

@plugin.route('/add_entry_dialog')
def add_entry_dialog():
    dialog = Dialog()
    txt = dialog.input('Add new entry (subreddit)')
    if txt:
        log("Adding {} to favorites".format(txt))
        ss = StreamingSubreddits()
        ss.add_entry(txt, txt)

@plugin.route('/delete_entry_dialog')
def delete_entry_dialog():
    ss = StreamingSubreddits()
    dialog = Dialog()
    entries = [i[0] for i in ss.get_all()]
    idx = dialog.contextmenu(entries)
    if idx >= 0:
        url = entries[idx]
        log("Deleting {} from favorites".format(url))
        ss.delete_entry(url)

@plugin.route('/reset_entries')
def reset_entries():
    log("Resetting to default favorites")
    ss = StreamingSubreddits()
    ss.reset_entries()

if __name__ == '__main__':
    plugin.run()
