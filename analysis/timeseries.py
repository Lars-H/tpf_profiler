#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 14:27:52 2017

@author: larsheling
"""
import matplotlib.pyplot as plt
from import_data import prepare_dataset

df = prepare_dataset()


pattern = "?s http://dbpedia.org/ontology/wikiPageWikiLink ?o."
#pattern = "?s ?p ?o."

df = df[(df['pattern'] == pattern) & (df['study_id'] == 58906) & (
    df['server'] == "http://aifb-ls3-vm8.aifb.kit.edu:3000/db")]

plt.scatter(df['timestamp'], df['ms'])
plt.show()
