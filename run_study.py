from core.profiler import Profiler
from sqlalchemy import create_engine
from optparse import OptionParser
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sources = {
    "local":
        {
            # Add address for the TPFs controlled environment
            "dbpedia": "http://aifb-ls3-vm8.aifb.kit.edu:3000/db",
            "geonames": "http://aifb-ls3-vm8.aifb.kit.edu:3000/geonames",
            "dblp": "http://aifb-ls3-vm8.aifb.kit.edu:3000/dblp",
            "wiktionary": "http://aifb-ls3-vm8.aifb.kit.edu:3000/wiktionary"
        },
    "remote":
        {
            # Addresses for the real-world TPFs
            "dbpedia": "http://data.linkeddatafragments.org/dbpedia2014",
            "geonames": "http://data.linkeddatafragments.org/geonames",
            "dblp": "http://data.linkeddatafragments.org/dblp",
            "wiktionary": "http://data.linkeddatafragments.org/wiktionary"
        }
}


def get_options():
    """
    Getting the command line options
    :return: options
    """
    parser = OptionParser()
    parser.add_option("-d", "--datasource", dest="datasource", type="string",
                      help="Name of datasource. \n Available: {0}".format(sources['local'].keys()), metavar="DATASORUCE")
    parser.add_option("-s", "--samples",
                      dest="samples", type="int", default=1,
                      help="Number of samples")
    parser.add_option("-r", "--runs",
                      dest="runs", type="int", default=1,
                      help="Number of runs per source")
    parser.add_option("-c", "--cached",
                      dest="caching", type="int", default=2,
                      help="Number of repeated requests")
    parser.add_option("-w", "--write",
                      dest="write", type="int", default=0,
                      help="Write to database")

    parser.add_option("--db_str",
                      dest="db_conn_str", type="string", default=None,
                      help="SQL Alchemy Engine DB connection string")

    (options, args) = parser.parse_args()
    return vars(options)


def run_study(**kwargs):
    """
    Running the profiler based on the args
    :param kwargs: Profiler options
    :return: None
    """
    db_connection_str = kwargs['db_conn_str']
    print(db_connection_str)
    remote = sources['remote'][kwargs['datasource']]
    local = sources['local'][kwargs['datasource']]
    repetition = kwargs['caching']
    if kwargs['write'] == 1:
        if not db_connection_str is None:
            engine = create_engine(db_connection_str)
        else:
            engine = None

    logger.info("Start study at " + str(datetime.now()))
    logger.info("Local: " + str(local))
    logger.info("Remote: " + str(remote))
    p = Profiler(server=local, alt_server=remote, runs=kwargs['runs'], total_samples=kwargs['samples'], samples_per_page=1,
                 repetitions=repetition, db_conn=engine, header={"accept": "application/ld+json"}, save=kwargs['write'])
    p.run()
    logger.info("Study finished")


if __name__ == '__main__':
    options = get_options()
    logger.info(options)
    run_study(**(options))
