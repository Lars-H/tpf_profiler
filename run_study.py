from core.profiler import Profiler
from sqlalchemy import create_engine
import logging
#logging.basicConfig(level=logging.INFO, filename="study.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_study():
    engine = create_engine('mysql://lhe:112358@localhost/moosqe')
    remote = "http://fragments.dbpedia.org/2015/en"
    local = "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"
    repetition = 2
    logger.info("Start study")
    Profiler.run_profiler(server=local, alt_server=remote , runs=20, total_samples=10, samples_per_page=1,
                           repetitions=repetition, db_conn=engine)
    logger.info("Study finished")

if __name__ == '__main__':
    run_study()