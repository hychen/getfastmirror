import ConfigParser
import os
import glob
import re

from aptsources import sourceslist as aptsources_sourceslist

__DEBUG__ = True

class InvaldeAction(Exception): pass
class FiltersNotFound(Exception):   pass

class RuleEntry(object):
    #{{{attrs
    name = None
    file = None
    action = None
    type = None
    uri = None
    dist = None
    comps = []
    #}}}

    #{{{def __str__(self):
    def __str__(self):
        return "Rule %s has %d conditions in %s" % (self.name, self.count, self.file)
    #}}}
pass

class RulesList(object):
    """Rules list
    """
    VALIDE_ACTIONS = ('enable', 'disable')
    #{{{def __init__(self, path):
    def __init__(self, path):
        self.list = []
        self.path = path
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(path)
        self._parse_entries()
    #}}}

    #{{{def _parse_entries(self):
    def _parse_entries(self):
        for sec in self.parser.sections():
            rule = RuleEntry()
            rule.name = sec
            rule.file = self.path
            if self.parser.has_option(sec, 'action'):
                rule.action = self.parser.get(sec, 'action')
                if rule.action not in self.VALIDE_ACTIONS:
                    raise InvalideAction()
            if self.parser.has_option(sec, 'type'):
                rule.type = self.parser.get(sec, 'type')
            if self.parser.has_option(sec, 'dist'):
                rule.dist = re.compile(self.parser.get(sec, 'dist'))
            if self.parser.has_option(sec, 'uri'):
                rule.uri = re.compile(self.parser.get(sec, 'uri'))
            if self.parser.has_option(sec, 'comps'):
                rule.comps = re.split('\s*', self.parser.get(sec, 'comps'))
            rule.count = len(self.parser.options(sec)) - 1
            self.list.append(rule)
    #}}}

    #{{{def __iter__(self):
    def __iter__(self):
        for e in self.list:
            yield e
        raise StopIteration
    #}}}

pass

class SourcesList(aptsources_sourceslist.SourcesList):
    """Enhancement of SourcesList class of Python-APT
    """
    #{{{def refresh(self, root=None):
    def refresh(self, root=None):
        """ update the list of known entries """
        if not root:
            super(SourcesList, self).refresh()
        else:
            self.list = []
            # read sources.list
            file = os.path.join(root, 'sources.list')
            self.load(file)
            # read sources.list.d
            partsdir = os.path.join(root, 'sources.list.d')
            for file in glob.glob("%s/*.list" % partsdir):
                self.load(file)
            # check if the source item fits a predefined template
            for source in self.list:
                if not source.invalid:
                    self.matcher.match(source)
    #}}}

    #{{{def apply_filters(self, filters):
    def apply_filters(self, filters):
        for rule in filters:
            for entry in self.list:
                self._debug(entry)
                valid_count = 0
                if rule.type and rule.type == entry.type:
                    valid_count += 1
                if rule.uri and rule.uri.match(entry.uri):
                    self._debug("uri ok")
                    valid_count += 1
                if rule.dist and rule.dist.match(entry.dist):
                    self._debug("dist ok")
                    valid_count += 1
                if rule.comps and rule.comps == entry.comps:
                    self._debug("comp ok")
                    valid_count += 1

                self._debug("Equals conditons %s/%s" % (valid_count , rule.count))
                if valid_count == rule.count:
                    if rule.action == 'enable':
                        entry.set_enabled(True)
                    elif rule.action == 'disable':
                        entry.set_enabled(False)
    #}}}

    #{{{def _debug(self, msg):
    def _debug(self, msg):
        if __DEBUG__:
            print msg
    #}}}
pass
