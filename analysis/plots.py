import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def plot_results(file, x, y):


    fig, ax = plt.subplots()
    df = pd.read_csv(file)
    df['elapsed'] = pd.to_timedelta(df['elapsed'])
    df['elapsed'] = df['elapsed']/np.timedelta64(1, 's')
    #df = df.groupby( ['subject', 'predicate', 'object'], axis=0).mean()
    df['id'] = str(df['id'].str.split("?"))
    df = df.groupby(['id'], axis=0).mean()


    print(df.head(1))
    print(df['Unnamed: 0'])
    plt.scatter(df['results'], df[y])

    plt.show()


if __name__ == '__main__':


    file = "/Users/larsheling/Documents/Development/moosqe/study/test.csv"
    plot_results(file, "id", "elapsed")
    
    