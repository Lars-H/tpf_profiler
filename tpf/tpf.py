import requests



#url ="http://fragments.dbpedia.org/2014/en?subject=&predicate=&object=http%3A%2F%2Fdbpedia.org%2Fresource%2FHardtwald"
server = "http://fragments.dbpedia.org/2014/en"


def get_pattern(server , **kwargs):

    payload = kwargs['payload']
    r = requests.get(server, params=payload)
    print(r.url)



if __name__ == '__main__':

    payload = {}
    payload['subject'] = ""
    payload['predicate'] = ""
    payload['object'] = "http://dbpedia.org/resource/Hardtwald"

    result = get_pattern(server, payload=payload)
    print(result)