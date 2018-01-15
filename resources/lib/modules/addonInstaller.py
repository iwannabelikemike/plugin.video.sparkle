# -*- coding: utf-8 -*-
import os
import xbmc, xbmcaddon
import control
import urllib
import zipfile

from dialogProgress import DialogProgress
from fileUtils import getFileContent, clearDirectory
from regexUtils import findall

PACKAGE_DIR = "special://home/addons/packages/"
INSTALL_DIR = "special://home/addons/"


DICT = {
        'plexus': 'https://offshoregit.com/xbmchub/xbmc-hub-repo/raw/master/program.plexus/program.plexus-0.1.4.zip',
        'chrome_launcher' : 'https://offshoregit.com/natko1412/zips/plugin.program.chrome.launcher-1.1.5.zip',
        'youtube' : 'https://github.com/Kolifanes/plugin.video.youtube/releases/download/5.1.20.5/plugin.video.youtube-5.1.20.5.zip',
        'yatp'  : 'https://offshoregit.com/natko1412/zips/plugin.video.yatp-3.1.13.zip'
         }

def get_addons():
    a = [('Plexus','plexus','program.plexus', 'https://addons.tvaddons.ag/cache/images/21dce4067b818532f2862a3e66a707_icon.png'),
        ('Chrome Launcher', 'chrome_launcher', 'plugin.program.chrome.launcher', 'http://www.iconarchive.com/download/i38830/google/chrome/Google-Chrome.ico'),
        ('YouTube', 'youtube', 'plugin.video.youtube', 'http://ftp.vim.org/ftp/mediaplayer/xbmc/addons/helix/plugin.video.youtube/icon.png'),
        ('YATP', 'yatp', 'plugin.video.yatp', 'https://github.com/romanvm/kodi.yatp/blob/master/plugin.video.yatp/icon.png?raw=true')]
    return a

def install(key):
    entry = DICT[key]
    return _install_addon(entry)

def _install_addon(url):
    ri = AddonInstaller()
    compressed = ri.download(url)
    if compressed:
        addonId = ri.install(compressed)
        if addonId:
            xbmc.sleep(100)
            xbmc.executebuiltin('UpdateLocalAddons')
            xbmc.sleep(100)
            try:
                _N_ = xbmcaddon.Addon(id=addonId)
                control.infoDialog('Addon installed')
                return True
            except:
                pass
    return False

def isInstalled(addonId):
    try:
        _N_ = xbmcaddon.Addon(id=addonId)
        return True
    except:
        return False


class AddonInstaller:
    
    def download(self, url, destination=PACKAGE_DIR):
        try:
            dlg = DialogProgress()
            dlg.create('Sparkle - Installing external addon')
            destination = xbmc.translatePath(destination) + os.path.basename(url)
            def _report_hook(count, blocksize, totalsize):
                percent = int(float(count * blocksize * 100) / totalsize)
                dlg.update(percent, url, destination)
            fp, _ = urllib.urlretrieve(url, destination, _report_hook)
            return fp
        except:
            pass
        dlg.close()
        return ""

    def extract(self, fileOrPath, directory):
        try:               
            if not directory.endswith(':') and not os.path.exists(directory):
                os.mkdir(directory)
            zf = zipfile.ZipFile(fileOrPath)
            for _, name in enumerate(zf.namelist()):
                if name.endswith('/'):
                    path = os.path.join(directory, name)
                    if os.path.exists(path):
                        clearDirectory(path)
                    else:
                        os.makedirs(path, 0777)
                else:
                    outfile = open(os.path.join(directory, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()
            return zf.filelist

        except:
            pass

        return None
                        
    def install(self, filename):
        destination = xbmc.translatePath(INSTALL_DIR)
        files = self.extract(filename, destination)
        if files:
            addonXml = filter(lambda x: x.filename.endswith('addon.xml'), files)
            if addonXml:
                path = os.path.join(destination, addonXml[0].filename)
                content = getFileContent(path)
                addonId = findall(content, '<addon id="([^"]+)"')
                if addonId:
                    return addonId[0]
        return None
    
