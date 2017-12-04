import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import numpy as np

from import_data import prepare_dataset

df = prepare_dataset()

gdf = df.groupby(['category'], axis=0).mean()


plt.figure(1)
local = df[df['server'] == "http://aifb-ls3-vm8.aifb.kit.edu:3000/db"]
sns.boxplot(local['category'], local['ms'], hue=local['study_id'])
# plt.yscale('log')
plt.xticks(rotation=90)
plt.ylabel("Runtime (ms)")

categories = df['category'].unique()
study_ids = local['study_id'].unique()
stats = pd.DataFrame()
for study_id in study_ids:
    stat = local[(local['study_id'] == study_id)]['ms'].describe()
    stats[str(study_id) + "_local"] = stat


plt.figure(2)
remote = df[df['server'] == "http://fragments.dbpedia.org/2015/en"]

for study_id in study_ids:
    stat = remote[(remote['study_id'] == study_id)]['ms'].describe()
    stats[str(study_id) + "_remote"] = stat

sns.boxplot(remote['category'], remote['ms'], hue=remote['study_id'])
plt.yscale('log')
plt.xticks(rotation=90)

plt.figure(3)
sns.boxplot(df['category'], df['ms'], hue=df['server'])
plt.yscale('log')
plt.xticks(rotation=90)


plt.show()
