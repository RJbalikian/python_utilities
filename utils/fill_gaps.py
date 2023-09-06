import pandas as pd
import pathlib

def fill_gaps(datapath, group_cols=['API_NUMBER', 'TABLE_NAME'], sort_col='TOP' , target_col='Stratcode', target='dg', match_type='contains', export=None, verbose=False, print_results=False, return_both=False, **read_csv_kwargs):
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
    logsWithDG = pd.read_csv(datapath,  **read_csv_kwargs)

    out_logsWithDG = logsWithDG.copy()

    containsList = ['contains', 'in']
    fullMatchList = ['fullmatch', 'exact', 'full', 'match']


    wellLogsGrouped = logsWithDG.groupby(group_cols)
    if verbose:
        print("Number of wells:", wellLogsGrouped.ngroups)
    for sortCols, wellDF in wellLogsGrouped:
        #wellDF.sort_values(by=sort_col, inplace=True, ascending=True)

        if match_type.lower() in containsList:
            wellDF['isTarget'] = wellDF[target_col].str.contains(target, case=False, regex=False)
            wellDF['isTarget'].fillna(False, inplace=True)
        elif match_type.lower() in fullMatchList:
            wellDF['isTarget'] = wellDF[target_col].str.fullmatch(target, case=False)
            wellDF['isTarget'].fillna(False, inplace=True)
               
        firstTarget = False
        lastTarget = False

        for (currIndex, contains_target) in wellDF['isTarget'].items():
            if firstTarget==False:
                if contains_target:
                    firstTarget = currIndex
                    lastTarget = firstTarget
                    continue
            else:
                if contains_target:
                    lastTarget = currIndex
                    continue
            if contains_target and verbose:
                print('Fill identified in row:'+ currIndex)
            
            
        if firstTarget != False and firstTarget != lastTarget:
            for repInd in range(firstTarget, lastTarget):
                if target in str(out_logsWithDG.loc[repInd, target_col]) and target != str(out_logsWithDG.loc[repInd, target_col]):
                    pass
                else:
                    out_logsWithDG.loc[repInd, target_col] = target      
            if verbose:
                print(f'{sortCols}: Filling in from {firstTarget} to {lastTarget}')    
        else:
            if verbose:
                print(f"{sortCols}: No target value found")
    
    if print_results:
        #print(logsWithDG[target_col]==out_logsWithDG[target_col])
        pass
       
    if export is not None:
        if export == True:
            export = pathlib.Path(datapath).with_stem(pathlib.Path(datapath).stem+'_filled')
            out_logsWithDG.to_csv(export, index_label='ID')
        else:
           out_logsWithDG.to_csv(export, index_label='ID')

    if return_both:
        return logsWithDG, out_logsWithDG
    return out_logsWithDG