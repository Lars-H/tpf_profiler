import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import numpy as np

studies = [41014, 63952]
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

file = results_path + str(studies[1]) + ".csv"
fig, ax = plt.subplots()
df = pd.read_csv(file)

#df['ms'] = df['elapsed'].microsecond
df['ms'] = df['elapsed']
df['ms'] = df['ms'].map( lambda x: int(str(x).split(".")[1]))

df['category'] = df['pattern'].map(lambda x: categorize(x)).astype("category")

gdf = df.groupby(['category'], axis=0).mean()
#gdf = df
#gdf.reset_index(drop=True, inplace=True)


plt.figure(1)
local = df[df['server'] == "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"]
sns.boxplot(local['category'], local['ms'])
plt.yscale('log')
plt.xticks(rotation=90)

plt.figure(2)
remote = df[df['server'] == "http://fragments.dbpedia.org/2015/en"]
sns.boxplot(remote['category'], remote['ms'])
plt.yscale('log')
#plt.scatter(gdf.index, gdf['ms'], c=np.log( gdf['total_items']))
plt.xticks(rotation=90)

plt.show()



