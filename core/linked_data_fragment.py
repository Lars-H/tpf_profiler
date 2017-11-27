import requests
import datetime as dt
import math
from pprint import pprint
from rdf_terms import *
import random

import logging as log
log.basicConfig(level=log.ERROR)


def get_pattern(server, triple_pattern, **kwargs):
    """
    Contact a LDF to get TPF
    :param server: Endpoint URL
    :param kwargs: Payload and Header
    :return: requests response
    """
    page = kwargs.get("page", 1)
    payload = {
        "subject" : triple_pattern.subject,
        "predicate" : triple_pattern.predicate,
        "object" : triple_pattern.object,
        "page" : page
    }
    log.info("Pattern: " + str(triple_pattern))
    log.info("Page: " + str(page))
    headers = kwargs.get('headers', {"accept": "application/json"})
    result = requests.get(server, params=payload, headers=headers)
    return result


def get_random_triples(result, n, no_literals=True):
    """
    Get n random triples from a result
    :param result: Requests response
    :param n: number of triples
    :return: Set of TriplePatterns
    """
    data = result.json()
    namespaces = data['@context']
    graph = data['@graph']
    triples = triples_from_graph(graph, namespaces)
    idx = [i for i in range(len(triples))]
    random.shuffle(idx)
    random_triples = []
    for i in idx:
        if not triples[i].contains_literal and no_literals:
            random_triples.append(triples[i])
        if len(random_triples) == n:
            break
    return random_triples


def triples_from_graph(graph, namespaces):

    results = []
    for item in graph:
        if "@graph" in item.keys():
            metadata = item['@graph']
        else:
            results.append(item)
    triples = []
    for result in results:
        subject = URI(result['@id'], namespaces = namespaces)

        for predicate in result.keys():
            if predicate == '@id':
                continue
            elif predicate == '@type':
                objs = result[predicate]
                triples.extend(eval(subject, URI('rdf:type', namespaces=namespaces), objs, namespaces))
            else:
                objs = result[predicate]
                triples.extend(eval(subject, URI(predicate, namespaces=namespaces), objs, namespaces))

    log.info("Number of triples: " + str(len(triples)))
    #pprint(triples)
    return triples


def eval(subject, predicate, object, namespaces):

    triples = []
    if type(object) == dict:
        if '@id' in object.keys():
            obj = URI(object['@id'], namespaces=namespaces)
        elif '@value' in object.keys():
            obj = Literal(**object)
        triple = Triple(subject, predicate, obj)
        triples.append(triple)
    elif type(object) == list:
        for obj in object:
            triples.extend(eval(subject, predicate, obj, namespaces))
    else:
        triple = Triple(subject, predicate, Literal(**{"@value": object}))
        triples.append(triple)
    return triples

def get_metadata(result):
    """

    :param result:
    :return:
    """
    json_ld = result.json()
    url = result.url#.split("&page")[0]
    graph = json_ld['@graph']
    context = json_ld['@context']
    if len(json_ld) == 2:
        for subgraph in graph:
            if "@graph" in subgraph.keys():
                metadata = subgraph['@graph']
                for elem in metadata:
                    if elem['@id'] == url:
                        metadata = elem
                        log.info("Total results: " + str(metadata['hydra:totalItems']))
                        break
    else:
        metadata = graph
        for elem in metadata:
            if elem['@id'] == url:
                metadata = elem
                log.info("Total results: " + str(metadata['hydra:totalItems']))
                break
    if not 'metadata' in locals():
        metadata = {}
        metadata['@id'] = "none"
        metadata['hydra:totalItems'] = 0

    return metadata, context


def get_parsed_metadata(result):
    return parse_metadata(get_metadata(result)[0])


def parse_metadata(metadata):
    """
    Parse the metadata into a dict
    :param metadata:
    :return:
    """

    mapping = {
        "itemsPerPage" : "hydra:itemsPerPage",
        "triples" : "void:triples"
    }
    meta_dict = {}
    for key, value in mapping.items():
        meta_dict[key] = metadata[value]

    meta_dict['pages'] = int(math.ceil(( meta_dict['triples'] / meta_dict['itemsPerPage'])))
    return meta_dict



def sample_ldf(server, triple_pattern):

    headers = {
        "accept" : "application/json"
    }
    result = get_pattern(server, triple_pattern=triple_pattern, headers = headers)
    sample = {}
    meta = get_metadata(result)
    meta_triples = triples_from_graph([meta[0]], meta[1])
    sample['elapsed'] = str(result.elapsed)
    sample['timestamp'] = str(dt.datetime.now())
    sample['perPage'] = __predicate_value(meta_triples, "PerPage")
    sample['totalItems'] = __predicate_value(meta_triples, "totalItems")
    sample['vars'] = len(triple_pattern.variables)
    sample['pattern'] = str(triple_pattern)
    return sample


def __predicate_value(triples, p):

    for triple in triples:
        if p in str(triple.predicate):
            return str(triple.object.value)

if __name__ == '__main__':

    file = "/Users/larsheling/Documents/Development/moosqe/queries/triple_patterns/tp1"
    server = "http://fragments.dbpedia.org/2014/en"

    r = get_pattern(server, Triple(URI("rdf:type"), Variable("?p"), Variable("?o")))
    pprint(r.json())