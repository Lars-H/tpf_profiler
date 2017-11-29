from sqlalchemy import create_engine
import pandas as pd
import os.path



def export_study_results(study_id):

    engine = create_engine('mysql://lhe:112358@localhost/moosqe')
    query = """
    SELECT *
      FROM results
      WHERE study_id = {0};
    """.format(study_id)
    df = pd.read_sql(query, engine)
    project_dir =  os.path.abspath(os.pardir)
    df.to_csv( project_dir +"/data/results/" + str(study_id) + ".csv")


if __name__ == '__main__':
    export_study_results(52762)