from core.profiler import Profiler
from sqlalchemy import create_engine
from optparse import OptionParser
from datetime import datetime
import json
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

abs_path = os.path.dirname(os.path.realpath(__file__))
ABS_PATH = abs_path
# Load sources
with open(abs_path +  '/sources.json') as json_data:
    sources = json.load(json_data)

def get_options():
    """
    Getting the command line options
    :return: options
    """
    parser = OptionParser()
    parser.add_option("-d", "--datasource", dest="datasource", type="string",
                      help="Name of datasource. \n Available: {0}".format(sources['local'].keys()))
    parser.add_option("--url", dest="url", type="string",
                      help="URL for the Triple Pattern Fragment", default=None)
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
    parser.add_option("-e", action="store_true", dest="empty_answer")

    parser.add_option("--db_str",
                      dest="db_conn_str", type="string", default=None,
                      help="SQL Alchemy Engine DB connection string")

    parser.add_option("--sample-file",
                      dest="sample_file", type="string", default=None,
                      help="File containing the sampled triple pattern.")

    (options, args) = parser.parse_args()
    return vars(options)


def run_study(**kwargs):
    """
    Running the profiler based on the args
    :param kwargs: Profiler options
    :return: None
    """
    if kwargs['url'] is None:
        remote = sources['remote'][kwargs['datasource']]
        local = sources['local'][kwargs['datasource']]
    else:
        local = kwargs['url']
        remote = None
    repetition = kwargs['caching']

    # Setup Database access
    engine = None
    if kwargs['write'] == 1:
        db_connection_str = kwargs['db_conn_str']
        if not db_connection_str is None:
            engine = create_engine(db_connection_str)

    logger.info("Start study at " + str(datetime.now()))
    logger.info("Local: " + str(local))
    logger.info("Remote: " + str(remote))

    # Setup the profiler
    try:
        p = Profiler(server=local, alt_server=remote, runs=kwargs['runs'], total_samples=kwargs['samples'], samples_per_page=1,
                 repetitions=repetition, db_conn=engine, header={"accept": "application/ld+json"}, save=kwargs['write'], empty_answers=kwargs['empty_answer'],
                     sample_file=kwargs['sample_file'])
    except Exception as e:
        logger.error("Could not initalize the Profiler: \n{0}".format(e))

    # Run the Profiler
    try:
        p.run()
    except Exception as e:
        logger.error("An error has occured during the execution of the Profiler: \n {0}".format(e))
    logger.info("Study finished")


if __name__ == '__main__':
    options = get_options()
    logger.info("Options: {0}".format(options))
    run_study(**(options))
