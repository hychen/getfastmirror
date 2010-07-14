import commands
import optparse
import re

from aptsources import distro

from getfastmirror import sourceslist
from getfastmirror import utils

__DESC__ = "Get and update fast mirror of APT archive around you."
__VERSION__ = "%prog 0.2.4"

class Admin(object):
    "Console Managment"
    #{{{def __init__(self, argv):
    def __init__(self, argv):
        self.parser = optparse.OptionParser(version=__VERSION__, description=__DESC__)
        self.filters = []
        self._init_argv(argv)
        self.dist = distro.get_distro()
        self.sourceslist = sourceslist.SourcesList()
        self.dist.get_sources(self.sourceslist)
        if self.opts.etcroot:
            self.dist.sourceslist.refresh(self.opts.etcroot)
    #}}}

    #{{{def _init_argv(self, argv):
    def _init_argv(self, argv):
        self.parser.add_option('-r',
                               '--etcroot',
                               dest='etcroot',
                               help="path of /etc/apt root")
        self.parser.add_option('-f',
                               '--filters',
                               dest='filters',
                               help="filters")
        self.parser.add_option('-l',
                               '--locale',
                               dest='locale',
                               help="locale")
        self.parser.add_option('-t',
                               '--nearest',
                               action="store_true",
                               default=False,
                               dest='nearest',
                               help="filters")
        (self.opts, self.args) = self.parser.parse_args(argv)
    #}}}

    #{{{def prepare_filters(self):
    def prepare_filters(self):
        if self.opts.filters:
            filters_path =  re.split('\s*', self.opts.filters)
            for path in filters_path:
                self.filters.append(sourceslist.RulesList(path))
    #}}}

    #{{{def apply_filters(self):
    def apply_filters(self):
        if not self.filters:
            raise sourceslist.FiltersNotFound
        for filter in self.filters:
            self.sourceslist.apply_filters(filter)
    #}}}

    #{{{def run(self):
    def run(self):
        try:
            cmd = self.args[0]
        except IndexError:
            self.parser.print_help()
            exit()

        if cmd == 'update':
            self.prepare_filters()
            if self.filters:
                self.apply_filters()
            if self.opts.nearest:
                self.change_mirror_by_nearest()
            elif self.opts.locale:
                self.change_mirror_by_locale(self.opts.locale)
            self.update_sourceslist()
        else:
            self.parser.print_help()
    #}}}

    #{{{def change_mirror_by_nearest(self):
    def change_mirror_by_nearest(self):
        arch = commands.getoutput("dpkg --print-architecture")
        server = utils.get_fastserver(arch, self.dist)
        if not server:
            return False
        url = "http://%s/ubuntu/" % server
        self.dist.change_server(url)
    #}}}

    #{{{def change_mirror_by_locale(self):
    def change_mirror_by_locale(self, locale):
        code = utils.get_country_code(locale)
        if not code:
            return False
        url = "http://%s.archive.ubuntu.com/ubuntu/" % code
        self.dist.change_server(url)
    #}}}

    #{{{def update_sourceslist(self):
    def update_sourceslist(self):
        self.dist.sourceslist.backup()
        self.dist.sourceslist.save()
    #}}}
pass
