import threading

from getfastmirror import mirror_test

#{{{def get_country_code(locale):
def get_country_code(locale):
    a = locale.find("_")
    z = locale.find(".")
    if z == -1:
        z = len(locale)
    return locale[a+1:z].lower()
#}}}

#{{{def get_fastserver(arch, distro):
def get_fastserver(arch, distro):
    event = threading.Event()
    event.set()
    test_file = "dists/%s/%s/binary-%s/Packages.gz" % \
                (distro.source_template.name,
                 distro.source_template.components[0].name,
                     arch)

    app = mirror_test.MirrorTest(distro.source_template.mirror_set.values(),
                                test_file, event)

    return app.run_full_test()
#}}}
