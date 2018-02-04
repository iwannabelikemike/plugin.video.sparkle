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
from resources.lib.modules.acesearch import acesearch, acestream_channels

addon = Addon('plugin.video.sparkle', sys.argv)
addon_handle = int(sys.argv[1])

plugin = routing.Plugin()

AddonPath = addon.get_path()
IconPath = os.path.join(AddonPath , "resources/media/")
fanart = os.path.join(AddonPath + "/fanart.jpg")

# Update path so that praw doesnt complain
sys.path.append(os.path.join(AddonPath, 'resources/lib/modules'))
from resources.lib.modules.subreddit_lists import streaming_subreddits
from resources.lib.modules.subreddits2 import subreddits

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
    # Add search
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(search),
        ListItem('TV Network Search'), True)
    # Add channel list
    addDirectoryItem(
        plugin.handle,
        plugin.url_for(channels),
        ListItem('Channel Streams'), True)
    endOfDirectory(plugin.handle)

@plugin.route('/subreddit/<subreddit_id>')
def show_subreddit(subreddit_id):
    sr = subreddits()
    for s in sr.events(subreddit_id):
        # Get the number of acestreams available for this event
        # Don't include it if there arent any available
        aces = [i for i in sr.event_links(s['submission_id']) if len(i['ace_links']) > 0]
        if len(aces) > 0:
            title = "{} ({} Stream)".format(s['title'], len(aces))
            addDirectoryItem(
                plugin.handle,
                plugin.url_for(show_event, s['submission_id']),
                ListItem(title), True)
    endOfDirectory(plugin.handle)

@plugin.route('/event/<submission_id>')
def show_event(submission_id):
    sr = subreddits()
    for l in sr.event_links(submission_id):
        if len(l['ace_links']) > 0:
            for a in l['ace_links']:
                #url='plugin://program.plexus/?url={a}&mode=2&name=Sparkle'.format(a=a)
                url = plugin.url_for(play, stream_url=a)
                addDirectoryItem(
                    plugin.handle,
                    url,
                    ListItem("{} - Quality: {} ({} upvotes)".format(a, l['quality'], l['score'])), True)
    endOfDirectory(plugin.handle)

@plugin.route('/play')
def play():
    stream_url = plugin.args['stream_url'][0]
    log("Playing {}".format(stream_url))
    try:
        xbmc.executebuiltin(AS_LAUNCH_LINK.format(url=stream_url, name='sparkle'))
    except Exception as inst:
        log(inst)

@plugin.route('/search')
def search():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    k = xbmc.Keyboard('', 'Search') ; k.doModal()
    q = k.getText() if k.isConfirmed() else None
    if (q == None or q == ''): return
    url = plugin.url_for(run_search, term=q)
    xbmc.executebuiltin('Container.Update(%s)' % url)


@plugin.route('/run_search/<term>')
def run_search(term):
    results = acesearch(term)
    for r in results:
        url = plugin.url_for(play, stream_url=r['url'])
        addDirectoryItem(plugin.handle, url, ListItem(r['desc']), True)
    endOfDirectory(plugin.handle)

@plugin.route('/channels')
def channels():
    results = acestream_channels()
    for r in results:
        url = plugin.url_for(play, stream_url=r['url'])
        title = '[COLOR {color}]{desc}[/COLOR]'.format(
                    desc=r['desc'], color=r['color'])
        addDirectoryItem(plugin.handle, url, ListItem(title), True)
    endOfDirectory(plugin.handle)

if __name__ == '__main__':
    plugin.run()
