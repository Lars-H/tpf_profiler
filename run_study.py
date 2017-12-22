from core.profiler import Profiler
from sqlalchemy import create_engine
from optparse import OptionParser
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sources = {
    "local" :
        {
            "dbpedia" : "http://aifb-ls3-vm8.aifb.kit.edu:3000/db",
            "wikidata": "http://aifb-ls3-vm8.aifb.kit.edu:3000/wikidata",
            "geonames": "http://aifb-ls3-vm8.aifb.kit.edu:3000/geonames",
            "yago": "http://aifb-ls3-vm8.aifb.kit.edu:3000/yago",
            "dblp": "http://aifb-ls3-vm8.aifb.kit.edu:3000/dblp",
            "wiktionary" : "http://aifnb-ls3-vm8.aifb.kit.edu:3000/wiktionary"
        },
    "remote" :
        {
            "dbpedia" : "http://fragments.dbpedia.org/2015/en",
            "wikidata": "https://query.wikidata.org/bigdata/ldf",
            "geonames": "http://data.linkeddatafragments.org/geonames",
            "yago": None,
            "dblp": "http://data.linkeddatafragments.org/dblp",
            "wiktionary" : "http://data.linkeddatafragments.org/wiktionary"
        }
}

def get_options():
    parser = OptionParser()
    parser.add_option("-d", "--datasource", dest="datasource", type="string",
                    help="Name of datasource", metavar="DATASORUCE")
    parser.add_option("-s", "--samples",
                     dest="samples", type="int",default=1,
                      help="Number of samples")
    parser.add_option("-r", "--runs",
                     dest="runs", type="int",default=1,
                      help="Number of runs per source")
    parser.add_option("-c", "--cached",
                     dest="caching", type="int",default=2,
                      help="Number of repeated requests")
    parser.add_option("-w", "--write",
                     dest="write", type="int",default=0,
                      help="Write to database")

    (options, args) = parser.parse_args()
    return vars(options)

def run_study(**kwargs):

    remote = sources['remote'][kwargs['datasource']]
    local =  sources['local'][kwargs['datasource']]
    repetition = kwargs['caching']
    if kwargs['write'] == 1:
        engine = create_engine('mysql://lhe:112358@localhost/moosqe')
    else:
        engine = None

    logger.info("Start study at " + str(datetime.now()))
    logger.info("Local: " + str(local))
    logger.info("Remote: " + str(remote))
    p = Profiler(server=local, alt_server=remote, runs=kwargs['runs'], total_samples=kwargs['samples'], samples_per_page=1,
                 repetitions=repetition, db_conn=engine, header={"accept" : "application/ld+json"})
    p.run()
    logger.info("Study finished")


if __name__ == '__main__':
    options = get_options()
    logger.info(options)
    run_study(**(options))