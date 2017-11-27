import requests
from linked_data_fragment import *
from pprint import pprint
import random
import itertools
import logging as log
log.basicConfig(level=log.INFO)

class Profiler(object):


    @staticmethod
    def run_profiler(server, **kwargs):
        runs = kwargs.get("runs", 1)
        samples = kwargs.get("samples", 10)
        samples_per_page = kwargs.get("samples_per_page", 1)

        results = []
        for i in range(runs):
            samples = Profiler.get_random_triples(server, samples, samples_per_page)
            patterns = Profiler.generate_test_patterns(samples)
            results.extend(Profiler.retrieve_patterns(server, patterns))

        pprint(results)
        # TODO: Write triples to DataFrame
        # TODO: Wrtie DB-Connector to insert into MySQL DB


    @staticmethod
    def get_random_triples(server, total_samples, samples_per_page=1):
        assert total_samples >= samples_per_page
        spo = Triple(Variable("?s"), Variable("?p"), Variable("?o"))
        result = get_pattern(server, spo)
        metadata = get_parsed_metadata(result)
        triples = []

        # TODO: Variable number of samples based on the DB size

        while len(triples) < total_samples:
            page = random.randint(1, metadata['pages'])
            result = get_pattern(server, spo, page=page)
            triples.extend(get_random_triples(result, samples_per_page))
        return triples

    @staticmethod
    def generate_test_patterns(triples):
        triple_patterns = []
        for triple in triples:
            triple_patterns.extend(triple)
            triple_patterns.extend(Triple(triple.subject, triple.predicate, Variable("?o")))
            triple_patterns.extend(Triple(triple.subject, Variable("?p"), Variable("?o")))
            triple_patterns.extend(Triple(Variable("?s"), triple.predicate, Variable("?o")))
            triple_patterns.extend(Triple(Variable("?s"), triple.predicate, triple.object))
            triple_patterns.extend(Triple(Variable("?s"), Variable("?p"), triple.object))
            triple_patterns.extend(Triple(triple.subject, Variable("?p"), triple.object))

        #pprint(triple_patterns)
        return triple_patterns


    @staticmethod
    def retrieve_patterns(server, triple_patterns, shuffle=True):

        results = []
        random.shuffle(triple_patterns)
        for pattern in triple_patterns:
            results.append(sample_ldf(server, pattern))
        return results




if __name__ == '__main__':


    remote = "http://fragments.dbpedia.org/2014/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    server = local
    Profiler.run_profiler(server, samples=10, samples_per_page=2)