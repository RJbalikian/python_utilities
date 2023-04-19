import pandas as pd 
import numpy as np

#Check each column in df for whether it varies significantly from other columns (axis=0 will do this for rows)
def std_outliers(df, std_thresh=3, avg_kind='median', axis=1, **kwargs):
    std_df = df.std(axis=axis)

    if avg_kind.lower() == 'median':
        avg_df = df.median(axis=axis)
    elif avg_kind.lower() == 'mean':
        avg_df = df.mean(axis=axis)
    elif avg_kind.lower() == 'mode':
        avg_df = df.mode(axis=axis)
    elif avg_kind.lower() == 'geometric':
        avg_df = np.exp(np.log(df.prod(axis=axis))/df.notna().sum(axis=axis))
    else:
        print("Please run std_outliers again and enter one of the following for avg_kind: 'median', 'mean', 'mode', or 'geometric'")
        return

    #Calculate thresholds as values, based on std_thresh input
    std_df['std_thresh+'] = avg_df + std_df*std_thresh
    std_df['std_thresh-'] = avg_df - std_df*std_thresh

    #Get df with 
    df_clean = df[df.gt(std_df['std_thresh+'], axis=axis) & df.lt(std_df['std_thresh-'], axis=axis)]

    return df_clean
