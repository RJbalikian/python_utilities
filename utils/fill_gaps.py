import pandas as pd
import pathlib

def fill_gaps(datapath, group_cols=['API_NUMBER', 'TABLE_NAME'], sort_col='TOP' , target_col='Stratcode', target='dg', match_type='contains', export=None):
    """Function to fill gaps in table, specifically for use where top and bottom of an interval are known and the entire interval between is assumed to be similar. 

    Parameters
    ----------
    datapath : str or pathlike object
        Path to the data file to be read by pandas.read_csv()
    group_cols : str or list of strings, default=['API_NUMBER', 'TABLE_NAME'], optional
        Name of column (or columns) to be used to group individual wells together, by default ['API_NUMBER', 'TABLE_NAME']
    sort_col : str or list of strings, default='TOP', optional
        Name of column by which to sort the individual wells after they have been grouped, by default 'TOP'
    target_col : str, default='Stratcode', optional
        Name of column which contains the target description, by default 'Stratcode'
    target : str, default='dg', optional
        Str or regular expression used to match the target that will be used for the top and bottom of the interval, by default 'dg'
    match_type : str, {'contains', 'fullmatch'}, optional
        What type of match to use for finding the target in target_col. If 'contains', uses pandas.Series.str.contains(), 'fullmatch' or 'match' uses pandas.Series.str.fullmatch(), by default 'contains'
    export : str or pathlike object, by default=None, optional
        Export path to export filled table, by default None

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with gaps in target interval filled
    """
    logsWithDG = pd.read_csv(datapath,  sep='\t')

    out_logsWithDG = logsWithDG.copy()

    wellLogsGrouped = logsWithDG.groupby(group_cols)
    for sortCols, wellDF in wellLogsGrouped:
        wellDF.sort_values(by=sort_col, inplace=True, ascending=True)

        if match_type == 'contains':
            wellDF['isTarget'] = wellDF[target_col].str.contains(target, case=False)
        elif match_type == 'fullmatch' or match_type =='match':
            wellDF['isTarget'] = wellDF[target_col].str.fullmatch(target, case=False)
        
        firstTarget = False
        lastTarget = False

        for (currIndex, contains_target) in wellDF['isTarget'].items():
            if firstTarget==False:
                if contains_target:
                    firstTarget = currIndex
                    continue
            else:
                if contains_target:
                    lastTarget = currIndex
                    continue
        
        out_logsWithDG.loc[firstTarget:lastTarget, target_col] = target      
    
    if export is not None:
        if export == True:
            export = pathlib.Path(datapath).with_stem(pathlib.Path(datapath).stem+'_filled')
            out_logsWithDG.to_csv(export, index_label='ID')
        else:
           out_logsWithDG.to_csv(export, index_label='ID')
    return out_logsWithDG