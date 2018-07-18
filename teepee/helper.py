

def prepare_df(df):
    df['ms'] = df['elapsed']
    df['ms'] = df['ms'].map(lambda x: int(
        float(str(x).split(":")[2]) * 1000000))
    df['category'] = df['pattern'].map(lambda x: categorize(x))
    return df


# Function to categorize the data
def categorize(p):

    p = str(p)
    if "?s " in p:
        if "?p " in p:
            if " ?o" in p:
                return "<v,v,v>"
            else:
                return "<v,v,r>"
        else:
            if " ?o" in p:
                return "<v,r,v>"
            else:
                return "<v,r,r>"
    else:
        if "?p " in p:
            if " ?o" in p:
                return "<r,v,v>"
            else:
                return "<r,v,r>"
        else:
            if " ?o" in p:
                return "<r,r,v>"
            else:
                return "<r,r,r>"