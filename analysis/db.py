from sqlalchemy import create_engine
import pandas as pd
import os.path
import sys

engine = create_engine('mysql://lhe:112358@localhost/moosqe')

def export_study_results(study_ids):

    for study_id in study_ids:
        query = """
        SELECT *
          FROM results
          WHERE study_id = {0};
        """.format(study_id)
        df = pd.read_sql(query, engine)
        project_dir = os.path.abspath(os.pardir)
        df.to_csv(project_dir + "/data/results/" + str(study_id) + ".csv")


def get_study_id(date):

    query = """
    SELECT id
      FROM study
      WHERE timestamp > \"{0}\";
    """.format(date)

    print(query)
    df = pd.read_sql_query(str(query), engine)
    return list(df.id)

if __name__ == '__main__':
    #ids = get_study_id("2017-12-08 00:00:00")
    ids = [sys.argv[1]]
    print(ids)
    export_study_results(ids)
