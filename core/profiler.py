from time import sleep
from core.linked_data_fragment import *
import random
import logging
import datetime as dt
import pandas as pd
import urllib2, socket, urlparse
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Profiler(object):

    def __init__(self, **kwargs):

        self.kwargs = kwargs
        if "server" not in kwargs.keys():
            raise AttributeError
        self.server = kwargs.get("server", None)
        self.runs = kwargs.get("runs", 1)
        self.num_of_samples = kwargs.get("total_samples", 10)
        self.samples_per_page = kwargs.get("samples_per_page", 1)
        self.repetitions_per_pattern = kwargs.get("repetitions", 1)
        self.shuffle_patterns = kwargs.get("shuffle", True)
        self.alt_server = kwargs.get("alt_server", None)
        self.db_conn = kwargs.get("db_conn", None)
        self.header = kwargs.get("header", {"accept" : "application/json"} )
        if not self.db_conn is None:
            kwargs.pop("db_conn")
            kwargs.pop("header")
        # Get the servers ip addresses
        try:
            data = urllib2.urlopen(self.server)
            self.server_ip = socket.gethostbyname(urlparse.urlparse(data.geturl()).hostname)
        except urllib2.HTTPError as e:
            logger.error("Could not retrive IP address. \n{0}".format(str(e)))

        # Get alternative server IP
        alt_server_ip = None
        if not self.alt_server is None:
            try:
                data = urllib2.urlopen(self.alt_server)
                self.alt_server_ip = socket.gethostbyname(urlparse.urlparse(data.geturl()).hostname)
            except urllib2.HTTPError as e:
                logger.error("Could not retrive IP address. \n{0}".format(str(e)))
                self.alt_server_ip = "1.1"

        # Generate a study_id
        self.study_id = int(str(hash(dt.datetime.now()))[1:9])
        logger.info("Study ID: " + str(self.study_id))


        # If we have an alternative server with the identical data
        # We may add it for the pattern retrieval
        self.servers = [self.server]
        if not self.alt_server is None:
            self.servers.append(self.alt_server)



    def run(self):

        samples = self.get_random_triples()
        patterns = Profiler.generate_test_patterns(samples)
        results = []
        try:
            for i in range(self.runs):
                logger.info("Run: " + str(i + 1) + "/" + str(self.runs))
                t0 = dt.datetime.now()
                res = self.retrieve_patterns(patterns)
                if not self.db_conn is None:
                    df = pd.DataFrame(res)
                    df['run'] = i
                    df.to_sql("results", self.db_conn,
                              if_exists="append", index=False)
                results.extend(res)
                logger.info("Runtime: " + str(dt.datetime.now() - t0))
        except Exception as e:
            logger.exception(str(e))

        if not self.db_conn is None:
            self.save_run(samples)


    def save_run(self, samples):
        # Save study
        data = self.kwargs
        data['timestamp'] = dt.datetime.now()
        data['id'] = self.study_id
        data['shuffle'] = self.shuffle_patterns
        data['server_ip'] = str(self.server_ip)
        data['alt_server_ip'] = str(self.alt_server_ip)
        df = pd.DataFrame([self.kwargs])
        df.to_sql("study", self.db_conn, if_exists="append", index=False)

    # Save samples
        smpls = []
        for sample in samples:
            d = sample.dict
            d['study_id'] = self.study_id
            smpls.append(d)
        df = pd.DataFrame(smpls)
        df.to_sql("samples", self.db_conn, if_exists="append", index=False)


    def get_random_triples(self):
        assert self.num_of_samples >= self.samples_per_page
        spo = Triple(Variable("?s"), Variable("?p"), Variable("?o"))
        result = get_pattern(self.server, spo, headers=self.header)
        #pprint(result.json())
        metadata = get_parsed_metadata(result)
        triples = set()

        # TODO: Variable number of samples based on the LDF size

        while len(triples) < self.num_of_samples:
            page = random.randint(1, metadata['pages'])
            result = get_pattern(self.server, spo, page=page, headers=self.header)
            triples.update(get_random_triples(result, self.samples_per_page))

        logger.info("Samples generated from TPF: " + str(len(triples)))
        return triples

    def retrieve_patterns(self, triple_patterns):

        triple_patterns = list(triple_patterns)
        if not type(self.servers) is list:
            servers = [self.servers]

        results = []
        if self.shuffle_patterns:
            random.shuffle(triple_patterns)
        for pattern in triple_patterns:
            for server in self.servers:
                for i in range(self.repetitions_per_pattern):

                    try:
                        results.append(sample_ldf(server, pattern, repetition=i, id=self.study_id, header=self.header))
                    except ConnectionError as conn_error:
                        # In Case of a Connection error
                        logger.error("Connection Error: " + str(conn_error))
                        logger.info(
                            "Server {0}, pattern {1}".format(server, pattern))

                        # Use Timeout and then try to continue
                        logger.info("Sleeping")
                        sleep(20)
                        logger.info("Continue")
        return results


    def patterns_per_sample(self, n):
        """
        Function to get the number of unique triple patterns based
        on a smaple of size n
        :param n: Sample size
        :return: number of unique triple patterns
        """
        self.num_of_samples = n
        samples = self.get_random_triples()
        patterns = Profiler.generate_test_patterns(samples)
        return len(patterns)


    @staticmethod
    def generate_test_patterns(triples):
        triple_patterns = set()
        for triple in triples:
            triple_patterns.add(triple)
            triple_patterns.add(
                Triple(triple.subject, triple.predicate, Variable("?o")))
            triple_patterns.add(
                Triple(triple.subject, Variable("?p"), Variable("?o")))
            triple_patterns.add(
                Triple(Variable("?s"), triple.predicate, Variable("?o")))
            triple_patterns.add(
                Triple(Variable("?s"), triple.predicate, triple.object))
            triple_patterns.add(
                Triple(Variable("?s"), Variable("?p"), triple.object))
            triple_patterns.add(
                Triple(triple.subject, Variable("?p"), triple.object))

        logger.info("Number of unique patterns: " + str(len(triple_patterns)))

        triple_patterns = list(triple_patterns)
        # For every pattern add one spo
        for i in range(len(triples)):
            triple_patterns.append(
                Triple(Variable("?s"), Variable("?p"), Variable("?o")))

        return triple_patterns



if __name__ == '__main__':

    remote = "http://fragments.dbpedia.org/2015/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    db = "https://query.wikidata.org/bigdata/ldf"
    server = db
    p = Profiler(server=local, samples=2,
                          samples_per_page=2, alt_server=remote, log=True, header={"accept": "application/ld+json"})

    for n in [100000]:
        result = p.patterns_per_sample(n)
        print("Samples: {0} -> Unique triple patterns: {1}".format(n, result))

    #p.run()

