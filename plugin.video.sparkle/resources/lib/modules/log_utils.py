"""
    tknorris shared module
    Copyright (C) 2016 tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import cProfile
import StringIO
import pstats
import json

try:
    import xbmc
    from xbmc import LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, LOGNONE, LOGNOTICE, LOGSEVERE, LOGWARNING  # @UnusedImport
    NAME = control.addonInfo('name')
    LOCAL_RUN = False
except:
    import logging
    # Use "local" logging
    LOGDEBUG = logging.DEBUG
    LOGERROR = logging.ERROR
    LOGFATAL = logging.FATAL
    LOGINFO = logging.INFO
    LOGNOTICE = logging.INFO
    LOGSEVERE = logging.CRITICAL
    LOGWARNING = logging.WARNING
    NAME = 'LOCAL_LOGGER'
    LOCAL_RUN = True

def log(msg, level=LOGDEBUG):
    req_level = level
    if LOCAL_RUN:
        logger = logging.getLogger()
        logger.setLevel(level)
    else:
        # override message level to force logging when addon logging turned on
        if control.setting('addon_debug') == 'true' and level == LOGDEBUG:
            level = LOGNOTICE
    try:
        if isinstance(msg, unicode):
            msg = '{} (ENCODED)'.format(msg.encode('utf-8'))
        txt = '[{}] {}'.format(NAME, msg)
        if LOCAL_RUN:
            logging.debug(txt)
        else:
            xbmc.log(txt, level)


    except Exception as e:
        msg = 'Logging Failure: {}'.format(e)
        if LOCAL_RUN:
            logging.error(msg)
        else:
            xbmc.log(msg, level)

class Profiler(object):
    def __init__(self, file_path, sort_by='time', builtins=False):
        self._profiler = cProfile.Profile(builtins=builtins)
        self.file_path = file_path
        self.sort_by = sort_by

    def profile(self, f):
        def method_profile_on(*args, **kwargs):
            try:
                self._profiler.enable()
                result = self._profiler.runcall(f, *args, **kwargs)
                self._profiler.disable()
                return result
            except Exception as e:
                log('Profiler Error: %s' % (e), LOGWARNING)
                return f(*args, **kwargs)

        def method_profile_off(*args, **kwargs):
            return f(*args, **kwargs)

        if _is_debugging():
            return method_profile_on
        else:
            return method_profile_off

    def __del__(self):
        self.dump_stats()

    def dump_stats(self):
        if self._profiler is not None:
            s = StringIO.StringIO()
            params = (self.sort_by,) if isinstance(self.sort_by, basestring) else self.sort_by
            ps = pstats.Stats(self._profiler, stream=s).sort_stats(*params)
            ps.print_stats()
            if self.file_path is not None:
                with open(self.file_path, 'w') as f:
                    f.write(s.getvalue())


def trace(method):
    def method_trace_on(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        log('{name!r} time: {time:2.4f}s args: |{args!r}| kwargs: |{kwargs!r}|'.format(name=method.__name__, time=end - start, args=args, kwargs=kwargs), LOGDEBUG)
        return result

    def method_trace_off(*args, **kwargs):
        return method(*args, **kwargs)

    if _is_debugging():
        return method_trace_on
    else:
        return method_trace_off


def _is_debugging():
    command = {'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.getSettings', 'params': {'filter': {'section': 'system', 'category': 'logging'}}}
    js_data = execute_jsonrpc(command)
    for item in js_data.get('result', {}).get('settings', {}):
        if item['id'] == 'debug.showloginfo':
            return item['value']

    return False

def execute_jsonrpc(command):
    from resources.lib.modules import control
    if not isinstance(command, basestring):
        command = json.dumps(command)
    response = control.jsonrpc(command)
    return json.loads(response)
