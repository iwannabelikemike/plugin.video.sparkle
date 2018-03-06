This is a fork of the Sparkle Kodi plugin that can be used to find acestream links from the Soccerstreams subreddit. Note that you need Acestream and Plexus installed in Kodi to use it.

This version is purely for acestream links posted in /r/soccerstreams.

This addon does not provide any content whatsoever, it is merely a method of scraping acestream links into Kodi to save copy/pasting them into Plexus.

Addon credit to: https://github.com/iwannabelikemike

Developing initial support for quality to be display in menus: https://github.com/TheCannings

I have included the Plexus addon and repo that can be installed.

Addons can be downloaded from the releases section of this repo. 

Simply download the ZIP folders to the Kodi device, then install from Addons -> Install from zip file

For Raspberry Pi, an updated version of Acestream can be installed. Connect to the Pi over SSH then:

cd ~/.kodi/userdata/addon_data/program.plexus

sudo rm -r acestream

wget https://github.com/jackyaz/plugin.video.sparkle/releases/download/1.1.0/acestream3121.tar.gz

tar xfv acestream3121.tar.gz
