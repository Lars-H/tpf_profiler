import logging as log
logger = log.getLogger(__name__)
logger.setLevel(log.WARNING)
import pandas as pd
import datetime as dt
import threading
import os
import json
import sys
sys.path.insert(0, '/home/lhe/dev/moosqe/')
from core.profiler import Profiler
log.getLogger("profiler").setLevel(log.WARNING)

class Profiler_Thread(threading.Thread):

    def __init__(self, uri, sample_size, id, meta_data):
        self.id = id
        self._uri = uri
        self._sample_size = sample_size
        self._done = False
        self._progress = 0.0
        self.p = None
        self._meta = meta_data
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.abspath(os.path.join(self.path, os.pardir)) + "/webapp/results"
        log.info(self.path)
        super(Profiler_Thread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):


        self._execution_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        max_pages = 0
        if self._meta['backend'].lower() == "sparql":
            max_pages = 10000
            log.info("SPARQL backend, Limit Pages to {0}".format(max_pages))
        self.p = Profiler(server=self._uri, runs=1, total_samples=self._sample_size, samples_per_page=1,
                 repetitions=1, header={"accept": "application/ld+json"}, save=True, empty_answers=False,
                          output_directory=self.path, filename=self.id, max_sample_page=max_pages)

        self.p.run()
        self.save_meta()
        self._done = True


    def save_meta(self):
        filename = self.path + "/meta/{0}.json".format(self.id)

        meta = {
            "id" : self.id,
            "timestamp" : self._execution_time,
            "uri" : self._uri,
            "sample_size" : self._sample_size,
            "backend" : self._meta['backend'],
            "environment" : self._meta['environment']
        }

        with open(filename, 'w') as fp:
            json.dump(meta, fp)
        log.info("Save meta to JSON.")

    def stop(self):
        log.info("Stopping thread.")
        self._stop_event.set()

    @property
    def status(self):
        if not self.done:
            if self._visualizing: return "creating visulizations"
            else: return "running"
        else:
            return "done"

    @property
    def done(self):
        return self._done

    @property
    def progress(self):
        if not self.p is None:
            log.info("Count: {0}; Sample Size: {1}".format(self.p.request_count, self.p.total_requests))
            prog =  float(self.p.request_count) / float(self.p.total_requests)
            return round(prog, 2)*100
        else:
            return 0.0

    def stopped(self):
        log.info("Thread stopped.")
        return self._stop_event.is_set()


if __name__ == '__main__':

    p = Profiler_Thread("http://data.linkeddatafragments.org/dbpedia2014", 1)
    p.start()
    print(p.done)