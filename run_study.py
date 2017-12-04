from core.profiler import Profiler
from sqlalchemy import create_engine
import sys
import argparse
import logging
#logging.basicConfig(level=logging.INFO, filename="study.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_options():

    parser = argparse.ArgumentParser(
        description="Linked Data Fragment Profiler")

    # Study arguments.
    parser.add_argument("-s1", "--server1",
                        help="URL of the triple pattern fragment server (required)")
    parser.add_argument("-s2", "--server2",
                        help="URL of an addtional triple pattern fragment server (optional)")
    parser.add_argument("-t", "--total_samples",
                        help="number of total samples",
                        type = int,
                        default = 1)
    parser.add_argument("-r", "--runs",
                        help="number of repeated experiments",
                        type = int,
                        default = 1)
    parser.add_argument("-c", "--repetitions",
                        help="Number of immediate repetitions",
                        type = int,
                        default = 1)
    parser.add_argument("-p", "--per_page",
                        help="SPARQL query (required, or -f)",
                        type = int,
                        default = 1)
    args = parser.parse_args()

    # Handling mandatory arguments.
    err = False
    msg = []
    if not args.server:
        err = True
        msg.append(
            "error: no server specified. Use argument -s to specify the address of a server.")

    if not args.file and not args.query:
        err = True
        msg.append(
            "error: no query specified. Use argument -f or -q to specify a query.")

    if err:
        parser.print_usage()
        print "\n".join(msg)
        sys.exit(1)

    return args.server, args.file, args.query, args.eddies, args.timeout, args.results, args.policy


def run_single_server(server):
    engine = create_engine('mysql://lhe:112358@localhost/moosqe')
    logger.info("Start study")
    Profiler.run_profiler(server=server, runs=50, total_samples=10, samples_per_page=1,
                          repetitions=2, db_conn=engine)
    logger.info("Study finished")


def run_study():
    engine = create_engine('mysql://lhe:112358@localhost/moosqe')
    remote = "http://fragments.dbpedia.org/2015/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    repetition = 2
    logger.info("Start study")
    Profiler.run_profiler(server=local, alt_server=remote, runs=10, total_samples=100, samples_per_page=1,
                          repetitions=repetition, db_conn=engine)
    logger.info("Study finished")


if __name__ == '__main__':
    run_study()
    # run_single_server("http://data.linkeddatafragments.org/geonames")
