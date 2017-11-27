import time
import linked_data_fragment as tpf
from random import shuffle
import pandas as pd

class Study(object):


    def __init__(self, server, tps, **kwargs):


        self.server = server
        self.tps = tps
        self.runs = kwargs.get('runs', 1)
        self.sleep = kwargs.get('sleep', 1)
        self.order = kwargs.get('order', 'lin')
        self.results = []
        self.__save = kwargs.get('save', False)

    def run(self):

        for i in range(self.runs):
            if self.order == "random":
                shuffle(self.order)

            for tp in self.tps:
                result = tpf.sample_ldf(self.server, tp)
                self.__add_result(result)
                time.sleep(self.sleep)

        if self.__save:
            self.__save_results()


    def __add_result(self, result):
        data = {}
        data['id'] = result['meta']['@id']
        data['results'] = result['meta']['hydra:totalItems']
        result.pop('meta', None)
        data.update(result)
        self.results.append(data)

    def __save_results(self):

        df = pd.DataFrame(self.results)
        df.to_csv("test.csv")
        print(df.head())


if __name__ == '__main__':

    remote = "http://fragments.dbpedia.org/2014/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    server = local
    path = "/Users/larsheling/Documents/Development/moosqe/queries/triple_patterns/"