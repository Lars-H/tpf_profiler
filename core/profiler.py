from time import sleep
from core.tpf_interface import *
import random
import logging
import datetime as dt
import pandas as pd
import urllib2
import socket
import urlparse
import os
from random import randint
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Profiler(object):

    def __init__(self, **kwargs):
        """
        Initialize the profiler
        :param kwargs:
        """
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
        self.save = kwargs.get("save", False)
        self.header = kwargs.get("header", {"accept": "application/json"})
        self.pages = kwargs.get("pages", None)
        if not self.pages is None:
            self.pages = [1, self.pages] # Definng the page range
        self.empty_answers = kwargs.get("empty_answers", False)
        self.sample_file = kwargs.get("sample_file", None)
        self._requests = 0
        self._total_requests = 1
        # Remove kwargs not to be saved in the results
        if not self.db_conn is None:
            kwargs.pop("empty_answers")
            kwargs.pop("db_conn")
            kwargs.pop("header")
            kwargs.pop("save")
            if "pages" in kwargs.keys():
                kwargs.pop("pages")
        # Get the servers ip addresses
        try:
            data = urllib2.urlopen(self.server)
            self.server_ip = socket.gethostbyname(
                urlparse.urlparse(data.geturl()).hostname)
        except urllib2.HTTPError as e:
            logger.error("Could not retrive IP address. \n{0}".format(str(e)))

        # Get alternative server IP
        if not self.alt_server is None:
            try:
                data = urllib2.urlopen(self.alt_server)
                self.alt_server_ip = socket.gethostbyname(
                    urlparse.urlparse(data.geturl()).hostname)
            except urllib2.HTTPError as e:
                logger.error(
                    "Could not retrive IP address. \n{0}".format(str(e)))
                self.alt_server_ip = "1.1"

        # Generate a study_id
        self.study_id = int(dt.datetime.now().strftime("%Y%m%d%H%M%S"))
        logger.info("Study ID: " + str(self.study_id))

        # If we have an alternative server with the identical data
        # We may add it for the pattern retrieval
        self.servers = [self.server]
        if not self.alt_server is None:
            self.servers.append(self.alt_server)

    def run(self):
        """
        Run the profiler
        :return:
        """
        if self.sample_file is None:
            samples = self.get_random_triples()
            patterns = self.generate_test_patterns(samples)
            self._total_requests = len(patterns)
        else:
            patterns = self.read_file(self.sample_file)

        results = []
        try:
            for i in range(self.runs):
                logger.info("Run: " + str(i + 1) + "/" + str(self.runs))
                t0 = dt.datetime.now()
                res = self.retrieve_patterns(patterns)
                if self.save:
                    df = pd.DataFrame(res)
                    df['run'] = i
                    self.save_results(df)
                results.extend(res)
                logger.info("Runtime: " + str(dt.datetime.now() - t0))

            # If saving CSV,
        except Exception as e:
            logger.exception(str(e))
            raise e


    def save_results(self, df):
        """
        Saving the result either to a database or as a csv dump
        :param df: DataFrame to be saved
        :return: None
        """
        if not self.db_conn is None:
            df.to_sql("results", self.db_conn,
                      if_exists="append", index=False, chunksize=100)
            logger.info("Results saved to database: {0}".format(self.db_conn))
        else:
            path = os.path.dirname(os.path.realpath(__file__))
            path = os.path.abspath(os.path.join(path, os.pardir))
            print(path)
            filename = path + "/data/{0}.csv".format(self.study_id)
            df.to_csv(filename, mode='a', header=(df['run'].unique()[0] == 0))

            logger.info("Results saved to file: {0}".format(filename))

    def save_run(self, samples):
        """
        Saves Profiler metadata (samples) to DB
        :param samples: Samples of the study
        :return:
        """
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
        """
        Retrieves a random list of triples from the TPF
        :return: List of Triples
        """
        assert self.num_of_samples >= self.samples_per_page
        spo = Triple(Variable("?s"), Variable("?p"), Variable("?o"))
        result = get_pattern(self.server, spo, headers=self.header)
        metadata = get_parsed_metadata(result)
        triples = set()
        max_pages = metadata['pages']
        while len(triples) < self.num_of_samples:
            page = random.randint(1, max_pages)
            result = get_pattern(
                self.server, spo, page=page, headers=self.header)
            if not result is None:
                triples.update(get_random_triples(result, self.samples_per_page))
            else:
                logger.exception("Could not get page {0}.".format(page))

        logger.info("Samples generated from TPF: " + str(len(triples)))
        return triples

    def retrieve_patterns(self, triple_patterns):
        """
        Requests a set of triple pattern and records metadata
        :param triple_patterns: Triple Patterns to be requested
        :return: Results in form of metadata
        """
        triple_patterns = list(triple_patterns)
        if not type(self.servers) is list:
            self.servers = [self.servers]

        results = []
        if self.shuffle_patterns:
            random.shuffle(triple_patterns)
        failed_patterns = set()
        self._requests = 0
        for pattern in triple_patterns:
            for server in self.servers:
                for i in range(self.repetitions_per_pattern):
                    try:
                        if self.pages is None:
                            results.append(sample_page(
                                server, pattern, repetition=i, id=self.study_id, header=self.header))
                        else:
                            results.extend(sample_pages(
                                server, pattern, repetition=i, id=self.study_id, header=self.header, page_range=self.pages))
                        self._requests  += 1
                    except ConnectionError as conn_error:
                        # In Case of a Connection error
                        logger.error("Connection Error: " + str(conn_error))
                        logger.info(
                            "Server {0}, pattern {1}".format(server, pattern))

                        # Use Timeout and then try to continue
                        logger.info("Sleeping")
                        sleep(20)
                        logger.info("Continue")
                    except Exception as e:
                        logger.exception("Could not get pattern: {0}".format(pattern))
                        failed_patterns.add(pattern)
        if len(failed_patterns) > 0:
            logger.info("Failed patterns: \n {0}".format(failed_patterns))
            logger.info("Failed patterns count: {0}".format(len(failed_patterns)))

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

        patterns = self.generate_test_patterns(samples)
        return len(patterns)

    def generate_test_patterns(self, triples):
        """
        Generates a list of triple patterns from a list of triples
        :param triples: Triples
        :return: List of triple patterns
        """
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
        logger.info("Empty answers: {0}".format(self.empty_answers))
        unknwn = URI("http://example.org/unknown")
        for i in range(len(triples)):
            triple_patterns.append(
                Triple(Variable("?s"), Variable("?p"), Variable("?o")))
            if self.empty_answers:
                # Add a triple with no answers
                variant = randint(1,7)
                if variant == 1:
                    t = Triple(unknwn, Variable("?p"), Variable("?o"))
                elif variant == 2:
                    t = Triple(unknwn, unknwn, Variable("?o"))
                elif variant == 3:
                    t = Triple(unknwn, unknwn, unknwn)
                elif variant == 4:
                    t = Triple(Variable("?s"), unknwn, Variable("?o"))
                elif variant == 5:
                    t = Triple(Variable("?s"), unknwn, unknwn)
                elif variant == 6:
                    t = Triple(unknwn, Variable("?p"), unknwn)
                elif variant == 7:
                    t = Triple(Variable("?s"), unknwn, Variable("?o"))
                triple_patterns.append(t)

        return triple_patterns


    def read_file(self, file):
        """
        Reads a file with triple patterns.
        Patterns need to be seperated by "\n" and not contain a "." at the end

        :param file: File with triple patterns
        :return: List of triple pattern objects
        """
        patterns = []
        try:
            with open(file, 'r') as samples_file:
                for line in samples_file.readlines():
                    line = line.replace('\n', '')
                    splits = line.split(" ")
                    terms = []
                    for split in splits:
                        if split[0] == '"':
                            terms.append(split[1:])
                        elif split[-1] == '"':
                            terms.append(split[:-1])
                        else:
                            terms.append(split)

                    if len(terms) == 3:
                        pattern = Triple(RDF_term.get_term(terms[0]), RDF_term.get_term(terms[1]), RDF_term.get_term(terms[2]))
                        patterns.append(pattern)
                    else:
                        logger.info("Didn't read line: {0}".format(line))
            return patterns
        except Exception as e:
            raise e

    @property
    def request_count(self):
        return self._requests

    @property
    def total_requests(self):
        return self._total_requests