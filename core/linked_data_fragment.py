import requests
from requests import ConnectionError
import datetime as dt
import math
from core.rdf_terms import *
import random
from pprint import pprint

import logging as logger
logger.basicConfig(level=logger.ERROR)

def get_pattern(server, triple_pattern, **kwargs):
    """
    Contact a LDF to get TPF
    :param server: Endpoint URL
    :param kwargs: Payload and Header
    :return: requests response
    """
    page = kwargs.get("page", 1)
    payload = {
        "subject": triple_pattern.subject,
        "predicate": triple_pattern.predicate,
        "object": triple_pattern.object,
        "page": page
    }
    logger.info("Pattern: " + str(triple_pattern))
    logger.info("Page: " + str(page))
    headers = kwargs.get('headers', {"accept": "application/json"})
    try:
        result = requests.get(server, params=payload, headers=headers)
    except ConnectionError as conn_error:
        raise conn_error

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
    random_triples = set()
    for i in idx:
        if not triples[i].contains_literal and no_literals:
            try:
                random_triples.add(triples[i])
            except UnicodeEncodeError as e:
                continue
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
        subject = URI(result['@id'], namespaces=namespaces)

        for predicate in result.keys():
            if predicate == '@id':
                continue
            elif predicate == '@type':
                objs = result[predicate]
                triples.extend(
                    eval(subject, URI('rdf:type', namespaces=namespaces), objs, namespaces))
            else:
                objs = result[predicate]
                triples.extend(
                    eval(subject, URI(predicate, namespaces=namespaces), objs, namespaces))

    logger.info("Number of triples: " + str(len(triples)))
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
            try:
                triples.extend(eval(subject, predicate, obj, namespaces))
            except KeyError as e:
                logger.ERROR(str(e))
            except UnicodeEncodeError as e:
                break
    else:
        triple = Triple(subject, predicate, Literal(**{"@value": object}))
        triples.append(triple)
    return triples


def get_metadata(response):
    """
    Retrieve the metadata from a given response
    :param response: Response message
    :return: Tuple (metadata , context)
    """
    json_ld = response.json()
    url = response.url  # .split("&page")[0]
    graph = json_ld['@graph']
    context = json_ld['@context']
    if len(json_ld) == 2:
        for subgraph in graph:
            if "@graph" in subgraph.keys():
                metadata = subgraph['@graph']
                for elem in metadata:
                    if elem['@id'] == url:
                        metadata = elem
                        logger.info("Total results: " +
                                    str(metadata['hydra:totalItems']))
                        break

            #For wikidata results
            if subgraph['@id'] == response.url:
                metadata = subgraph
            #elif 'subset' in subgraph.keys() and  == response.url



    else:
        metadata = graph
        for elem in metadata:
            if elem['@id'] == url:
                metadata = elem
                logger.info("Total results: " +
                            str(metadata['hydra:totalItems']))
                break
    if not 'metadata' in locals():
        metadata = {}
        metadata['@id'] = "none"
        metadata['hydra:totalItems'] = 0

    return metadata, context


def get_parsed_metadata(result):
    return parse_metadata(get_metadata(result))


def parse_metadata(graph):
    """
    Parse the metadata into a dict
    :param metadata:
    :return:
    """
    metadata = graph[0]
    context = graph[1]
    #pprint(metadata)
    mapping = {
        "itemsPerPage": "hydra:itemsPerPage", # http://www.w3.org/ns/hydra/core#
        "triples": "void:triples"
    }
    """mapping_wikidata = {
        "itemsPerPage": "http://www.w3.org/ns/hydra/core#hydra:itemsPerPage",
        "triples": "void:triples"
    }"""
    #mapping = mapping_wikidata
    meta_dict = {}
    for key, value in mapping.items():
        meta_dict[key] = metadata[value]

    meta_dict['pages'] = int(
        math.ceil((meta_dict['triples'] / meta_dict['itemsPerPage'])))
    return meta_dict


def sample_ldf(server, triple_pattern, id=1, repetition=0, header={"accept": "application/json"}):
    """
    Samples a given pattern from the Linked Data Fragment and records
    the metadata
    :param server: Linked Data Fragment Server
    :param triple_pattern: Pattern to be requested
    :param id: Study ID
    :return: Dict with the corresponding metadata
    """
    # Check for connection errors
    try:
        result = get_pattern(
            server, triple_pattern=triple_pattern, headers=header)
    except ConnectionError as conn_error:
        raise conn_error

    sample = {}
    meta = get_metadata(result)
    meta_triples = triples_from_graph([meta[0]], meta[1])
    sample['study_id'] = id
    sample['elapsed'] = str(result.elapsed)
    sample['timestamp'] = str(dt.datetime.now())
    sample['perPage'] = __predicate_value(meta_triples, "PerPage")
    sample['total_items'] = __predicate_value(meta_triples, "totalItems")
    sample['vars'] = len(triple_pattern.variables)
    sample['pattern'] = str(triple_pattern)
    sample['server'] = server
    if repetition == 0:
        sample['cached'] = False
    else:
        sample['cached'] = True
    return sample


def __predicate_value(triples, p):

    for triple in triples:
        if p in str(triple.predicate):
            return str(triple.object.value)


if __name__ == '__main__':

    file = "/Users/larsheling/Documents/Development/moosqe/queries/triple_patterns/tp1"
    server = "http://fragments.dbpedia.org/2015/en"

    t = Triple(URI("dbpedia:Georgia_Turner"), Variable("?p"), Variable("?o"))
    r = get_pattern(server, t)
    data = r.json()
    namespaces = data['@context']
    graph = data['@graph']
    triples = triples_from_graph(graph, namespaces)
    pprint(triples)
