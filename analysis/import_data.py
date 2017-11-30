#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:33:09 2017

@author: larsheling
"""

import pandas as pd

def prepare_dataset():

    study_ids = [48878, 52762, 58906, 63952, 69518]
    results_path = "/Users/larsheling/Documents/Development/moosqe/data/results/"
    
    def categorize(p):
        
        p = str(p)
        if "?s" in p:
            if "?p" in p:
                if "?o" in p:
                    return "?s ?p ?o"
                else:
                    return "?s ?p bd"
            else:
                if "?o" in p:
                    return "?s bd ?o"
                else:
                    return "?s bd db"
        else:
            if "?p" in p:
                if "?o" in p:
                    return "bd ?p ?o"
                else:
                    return "bd ?p bd"
            else:
                if "?o" in p:
                    return "bd bd ?o"
                else:
                    return "bd bd bd"
    
    df = pd.DataFrame()
    
    studies = [results_path + str(study_ids[i]) + ".csv" for i in range(len(study_ids))]
    for study in studies:
        study_data = pd.read_csv(study)
        df = pd.concat([df, study_data])
    
    
    df['ms'] = df['elapsed']
    df['ms'] = df['ms'].map( lambda x: int(float(str(x).split(":")[2])*10000000))
    
    df['category'] = df['pattern'].map(lambda x: categorize(x)).astype("category")
    return df