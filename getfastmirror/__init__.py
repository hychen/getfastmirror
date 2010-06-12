# @author 2010 Hsin-Yi Chen (hychen)
import commands
import os
import threading

from aptsources import distro as apt_dist
from aptsources import sourceslist as apt_sourceslist

from getfastmirror import mirror_test
from getfastmirror import sourceslist

def get_fasturl(arch, distro):
    event = threading.Event()
    event.set()
    test_file = "dists/%s/%s/binary-%s/Packages.gz" % \
                (distro.source_template.name,
                 distro.source_template.components[0].name,
                     arch)

    app = mirror_test.MirrorTest(distro.source_template.mirror_set.values(),
                                test_file, event)

    return app.run_full_test()

def run():
    arch = commands.getoutput("dpkg --print-architecture")
    distro = apt_dist.get_distro()
    distro.get_sources(apt_sourceslist.SourcesList())
    f = sourceslist.APTsource(distro.codename)
    f.set_fasturl('http://'+get_fasturl(arch, distro))
    print f
