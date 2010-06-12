#!/usr/bin/env python
# the original code is from softwareproperties.
import threading, Queue, time, re, subprocess, tempfile
import aptsources
from timeit import Timer
import urllib2
import socket
import random

class MirrorTest(threading.Thread):
    """Determines the best mirrors by perfoming ping and download test."""
    class PingWorker(threading.Thread):
        """Use the command line command ping to determine the server's
           response time. Using multiple threads allows to run several
           test simultaneously."""
        def __init__(self, jobs, results, id, parent, borders=(0,1), mod=(0,0)):
            self.borders = borders
            self.mod = mod
            self.parent = parent
            self.id = id
            self.jobs = jobs
            self.results = results
            self.match_result = re.compile(r"^rtt .* = [\.\d]+/([\.\d]+)/.*")
            threading.Thread.__init__(self)
        def run(self):
            result = None
            while not self.jobs.empty() and self.parent.running.isSet():
                try:
                    mirror = self.jobs.get(False)
                    host = mirror.hostname

                    self.parent.report_action("Pinging %s..." % host)
                    commando = subprocess.Popen("ping -q -c 2 -W 1 -i 0.5 %s" % host,
                                                shell=True, stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT).stdout
                    while True:
                        line = commando.readline()
                        if not line:
                            break
                        result = re.findall(self.match_result, line)
                except Queue.Empty, e:
                    return
                except:
                    self.parent.report_action("Skipping %s" % host)
                # report and count the mirror (regardless of its success)
                MirrorTest.completed_lock.acquire()
                MirrorTest.completed += 1
                self.parent.report_progress(MirrorTest.completed,
                                            MirrorTest.todo,
                                            self.borders,
                                            self.mod)
                if result:
                    self.results.append([float(result[0]), host, mirror])
                MirrorTest.completed_lock.release()

    def __init__(self, mirrors, test_file, running=None):
        threading.Thread.__init__(self)
        self.test_file = test_file
        self.threads = []
        MirrorTest.completed = 0
        MirrorTest.completed_lock = threading.Lock()
        MirrorTest.todo = len(mirrors)
        self.mirrors = mirrors
        if not running:
            self.running = threading.Event()
        else:
            self.running = running

    def report_action(self, text):
        """Subclasses should override this method to receive
           action message updates"""
        print text

    def report_progress(self, current, max, borders=(0,100), mod=(0,0)):
        """Subclasses should override this method to receive
           progress status updates"""
        print "Completed %s of %s" % (current + mod[0], max + mod[1])

    def run_full_test(self):
        # Determinate the 5 top ping servers
        results_ping = self.run_ping_test(max=5, borders=(0, 0.5), mod=(0,7))

        # Add two random mirrors to the download test
        size = len(self.mirrors)
        if size > 2:
            results_ping.append([0, 0, self.mirrors[random.randint(1, size-1)]])
            results_ping.append([0, 0, self.mirrors[random.randint(1, size-1)]])
        results = self.run_download_test(map(lambda r: r[2], results_ping),
                                         borders=(0.5, 1),
                                         mod=(MirrorTest.todo,
                                              MirrorTest.todo))
        for (t, h) in results:
            print "mirror: %s - time: %s" % (h.hostname, t)
        if not results:
            return None
        else:
            winner = results[0][1].hostname
            print "and the winner is: %s" % winner
            return winner

    def run_ping_test(self, mirrors=None, max=None, borders=(0,1), mod=(0,0)):
        """Performs ping tests of the given mirrors and returns the
           best results (specified by max).
           Mod and borders could be used to tweak the reported result if
           the download test is only a part of a whole series of tests."""
        if mirrors == None:
            mirrors = self.mirrors
        jobs = Queue.Queue()
        for m in mirrors:
            jobs.put(m)
        results = []
        #FIXME: Optimze the number of ping working threads LP#90379
        for i in range(25):
            t = MirrorTest.PingWorker(jobs, results, i, self, borders, mod)
            self.threads.append(t)
            t.start()

        for t in self.threads:
            t.join()

        results.sort()
        return results[0:max]

    def run_download_test(self, mirrors=None, max=None, borders=(0,1),
                          mod=(0,0)):
        """Performs download tests of the given mirrors and returns the
           best results (specified by max).
           Mod and borders could be used to tweak the reported result if
           the download test is only a part of a whole series of tests."""
        def test_download_speed(mirror):
            url = "%s/%s" % (mirror.get_repo_urls()[0],
                             self.test_file)
            self.report_action("Downloading %s..." % url)
            start = time.time()
            try:
                data = urllib2.urlopen(url, timeout=2).read(102400)
                return time.time() - start
            except:
                return 0
        if mirrors == None:
            mirrors = self.mirrors
        results = []

        for m in mirrors:
            if not self.running.isSet():
                break
            download_time = test_download_speed(m)
            if download_time > 0:
                results.append([download_time, m])
            self.report_progress(mirrors.index(m) + 1, len(mirrors), (0.50,1), mod)
        results.sort()
        return results[0:max]
