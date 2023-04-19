import pandas as pd 
import numpy as np

#Check each column in df for whether it varies significantly from other columns (axis=0 will do this for rows)
def std_outliers(df, std_thresh=3, avg_kind='median', axis=1, **kwargs):
    """Function to remove outliers from dataframe (containing shoreline coordinates, in this case)

    Parameters
    ----------
    df : pandas.DataFrame
        Input pandas dataframe to clean up
    std_thresh : float, default=3.0
        Number multiplied by standard deviation to get threshold of what is considered an outlier, by default 3
    avg_kind : str {'median', 'mean', 'mode', 'geometric'}, default='median'
        What type of average/mean value to use (not for calculating std deviation, but for removing), by default 'median'
    axis : int, default=1
        Which axis to do all actions across. If 1, this will calculate standard devation across columns. If 0, will do so within columns, by default 1

    Returns
    -------
    df_clean : pandas.DataFrame
        Dataframe the same size as input df, but with outlier data replaced by np.nan
    """
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
