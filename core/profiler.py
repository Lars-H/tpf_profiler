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

    @staticmethod
    def run_profiler(**kwargs):
        if "server" not in kwargs.keys():
            raise AttributeError
        server = kwargs.get("server", None)
        runs = kwargs.get("runs", 1)
        samples = kwargs.get("total_samples", 10)
        samples_per_page = kwargs.get("samples_per_page", 1)
        repetitions_per_pattern = kwargs.get("repetitions", 1)
        shuffle_patterns = kwargs.get("shuffle", True)
        alt_server = kwargs.get("alt_server", None)
        db_conn = kwargs.get("db_conn", None)
        if not db_conn is None:
            kwargs.pop("db_conn")

        # Get the servers ip addresses
        data = urllib2.urlopen(server)
        server_ip = socket.gethostbyname(urlparse.urlparse(data.geturl()).hostname)

        # Get alternative server IP
        alt_server_ip = None
        if not alt_server is None:
            data = urllib2.urlopen(alt_server)
            alt_server_ip = socket.gethostbyname(urlparse.urlparse(data.geturl()).hostname)

        # Generate a study_id
        study_id = int(str(hash(dt.datetime.now()))[1:9])
        logger.info("Study ID: " + str(study_id))


        # If we have an alternative server with the identical data
        # We may add it for the pattern retrieval
        servers = [server]
        if not alt_server is None:
            servers.append(alt_server)

        samples = Profiler.get_random_triples(
            server, samples, samples_per_page)
        logger.info("Samples generated from TPF: " + str(len(samples)))
        patterns = Profiler.generate_test_patterns(samples)
        results = []
        try:
            for i in range(runs):
                logger.info("Run: " + str(i + 1) + "/" + str(runs))
                t0 = dt.datetime.now()
                res = Profiler.retrieve_patterns(
                    servers, patterns, shuffle=shuffle_patterns, repetitions=repetitions_per_pattern, id=study_id)
                if not db_conn is None:
                    df = pd.DataFrame(res)
                    df['run'] = i
                    df.to_sql("results", db_conn,
                              if_exists="append", index=False)
                results.extend(res)
                logger.info("Runtime: " + str(dt.datetime.now() - t0))
        except Exception as e:
            logger.exception(str(e))

        # Save study
        if not db_conn is None:
            data = kwargs
            data['timestamp'] = dt.datetime.now()
            data['id'] = study_id
            data['shuffle'] = shuffle_patterns
            data['server_ip'] = str(server_ip)
            data['alt_server_ip'] = str(alt_server_ip)
            df = pd.DataFrame([kwargs])
            df.to_sql("study", db_conn, if_exists="append", index=False)

        # Save samples
        if not db_conn is None:
            smpls = []
            for sample in samples:
                d = sample.dict
                d['study_id'] = study_id
                smpls.append(d)
            df = pd.DataFrame(smpls)
            df.to_sql("samples", db_conn, if_exists="append", index=False)




    @staticmethod
    def get_random_triples(server, total_samples, samples_per_page=1):
        assert total_samples >= samples_per_page
        spo = Triple(Variable("?s"), Variable("?p"), Variable("?o"))
        result = get_pattern(server, spo)
        metadata = get_parsed_metadata(result)
        triples = set()

        # TODO: Variable number of samples based on the LDF size

        while len(triples) < total_samples:
            page = random.randint(1, metadata['pages'])
            result = get_pattern(server, spo, page=page)
            triples.update(get_random_triples(result, samples_per_page))
        return triples

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

    @staticmethod
    def retrieve_patterns(servers, triple_patterns, shuffle=True, repetitions=1, id=1):

        triple_patterns = list(triple_patterns)
        if not type(servers) is list:
            servers = [servers]

        results = []
        if shuffle:
            random.shuffle(triple_patterns)
        for pattern in triple_patterns:
            for server in servers:
                for i in range(repetitions):

                    try:
                        results.append(sample_ldf(server, pattern, id, i))
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


if __name__ == '__main__':

    remote = "http://fragments.dbpedia.org/2014/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    server = local
    a = dt.datetime.now()
    Profiler.run_profiler(server=server, samples=2,
                          samples_per_page=2, alt_server=remote, log=True)
    print(str(dt.datetime.now() - a))
