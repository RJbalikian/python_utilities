import csv
import pathlib
import re
import xml

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

def vtk_reader(vtk_filepath, return_df=True):
    #Read file
    with open(vtk_filepath, 'r') as datafile:
        filereader = csv.reader(datafile)

        #Flags indicating row on which each section of file begins
        startLocs = 0
        startData = 0
        #Text indicator for start of file section
        startLocInd = 'POINTS'
        startDataInd = 'LOOKUP_TABLE'

        #Flags indicating row on which each section of file end
        endLocs = 0
        endData = 0
        #Indicator for end of file section
        endLocInd = []
        endDataInd = []

        #Lists that will hold text between each section of file (that more or less doesn't change)
        fileLead = []
        fileMid = []
        fileTail = []

        #Lists that will hold data
        vtkdata = []
        vtklocs = []

        #Initialize lists
        newrow = [] #THis may not need initializing
        xLocPts = []
        yLocPts = []
        zLocPts = []
        vPts = []

        #Go through each row and find the important stuff
        for row in enumerate(filereader):
            if startLocs == 0:
                fileLead.append(row[1])
                fileLead[row[0]] = fileLead[row[0]][:]
                if startLocInd in str(row[1]):
                    startLocs = 1
            elif startLocs == 1 and endLocs == 0:
                if endLocInd == row[1]:
                    endLocs = 1
                else:
                    newrow = re.split(' +', str(row[1][0]))
                    newrow = newrow[1:]
                    vtklocs.append(newrow)
            elif startData == 0:
                fileMid.append(row[1])
                if startDataInd in str(row[1]):
                    startData = 1
            elif startData == 1 and endData == 0:
                if row[1] == endDataInd:
                    endData == 1
                else:
                    newrow = re.split(' +', str(row[1][0]))
                    newrow = newrow[1:]
                    vtkdata.append(newrow)
            else:
                fileTail.append(row[1])
                fileTail[row[0]] = fileTail[row[0]][:]

    #xPtCols = np.arange(0, 1000, 3)
    #yPtCols = np.arange(1, 1000, 3)
    #zPtCols = np.arange(2, 1000, 3)
    
    xPtCols = [0,3,6,9] #The ones I am using are formatted like this, 
    yPtCols = [1,4,7,10]
    zPtCols = [2,5,8,11]

    for r in vtklocs:#For each row with locations
        Xs = 0.0
        for x in xPtCols:
            Xs = Xs + float(r[x])
        xLocPts.append(Xs/4.0)

        Ys = 0.0
        for y in yPtCols:
            Ys = Ys + float(r[y])
        yLocPts.append(Ys/4.0)

        Zs = 0.0
        for z in zPtCols:
            Zs = Zs + float(r[z])
        zLocPts.append(Zs/4)


    for d in vtkdata:
        for i in d:
            vPts.append(i)

    dataframeIN = pd.DataFrame([xLocPts, yLocPts, zLocPts, vPts]).transpose()
    dataframeIN.columns = ['X','Y','Z','Resistivity']
    dataframeIN['minElecSpacing'] = np.nanmin(dataframeIN['X'].diff())

    #Format vtk file
    fileHeaderDict = {}
    fileHeaderDict['Filename'] = pathlib.Path(vtk_filepath).as_posix()
    fileHeaderDict['Project'] = 'NA'
    fileHeaderDict['Array'] = 'NA'
    fileHeaderDict['minElectSpcng'] = str(round(dataframeIN.loc[1,'X'] - dataframeIN.loc[0,'X'],1))
    fileHeaderDict['DataPts'] = len(dataframeIN)
    
    if return_df:
        return dataframeIN

def soundings_to_vtk(input_data, xcol='X', ycol='Y', zcol='Z', datacol='Data'):

    

def xyz_to_dae(xyz_data, xcol='X', ycol='Y', zcol='Z', datacol='Data', dimensions=['x', 'z'], cmap='nipy_spectral', qhull_options='Qbb Qc Qz', export=None, plot_vor=False, clean_type='move'):
    if isinstance(xyz_data, pd.DataFrame):
        pass
    elif isinstance(xyz_data, str):
        xyz_data = pathlib.Path(xyz_data)
    
    if isinstance(xyz_data, pathlib.Path):
        xyz_data = pd.read_csv(xyz_data)
    elif isinstance(xyz_data, pd.DataFrame):
        pass
    else:
        raise RuntimeError("xyz_data must be str, pandas.DataFrame, pathlib.Path")
    
    #Add a sounding number that is the same for all values with the same x and y
    xyz_data['SoundingNum'] = xyz_data.groupby([xcol, ycol]).ngroup()
    xyz_data['SoundingMin'] = xyz_data.groupby([xcol, ycol])[zcol].transform('min')
    xyz_data['SoundingMax'] = xyz_data.groupby([xcol, ycol])[zcol].transform('max')


    x_coords = xyz_data[xcol]
    y_coords = xyz_data[ycol]
    z_coords = xyz_data[zcol]
    
    dimDict = {'x':x_coords,
               'y':y_coords,
               'z':z_coords}
    
    
    if isinstance(dimensions, str):
        dimensions = [dimensions]

    unusedDim = []
    dimList = []
    for dim in dimDict.keys():
        if dim in dimensions:
            dimList.append(dimDict[dim])
        else:
            unusedDim.append({dim:dimDict[dim]})

    xyz_coords = np.array(dimList).transpose()

    delauneyList = ['delauney', 'del', 'd']
    voronoiList = ['voronoi', 'vor', 'v']
    
    data = xyz_data[datacol]
    
    xyzVor = scipy.spatial.Voronoi(points=xyz_coords, qhull_options=qhull_options)

    #plot_vor=False
    if len(dimList) <= 2 and plot_vor:
        scipy.spatial.voronoi_plot_2d(xyzVor)

    cellCoords = []
    for pr in range(len(xyzVor.point_region)):
        currCoords = []
        currCoords = list(xyzVor.vertices[xyzVor.regions[xyzVor.point_region[pr]]])
        for i, c in enumerate(currCoords):
            currCoords[i] = list(c)
        cellCoords.append(currCoords)
    
    indDict = {'x':0,
               'y':1,
               'z':2}

    #x = []
    #z = []
    #For later cleaning up stuff
    max_dim0 = dimList[0].max()
    max_dim1 = dimList[1].max()
    min_dim0 = dimList[0].min()
    min_dim1 = dimList[1].min()

    #Insert the unused dimension back in so we have three dimensional vertices again with two-dimensional cells connecting them
    xyz_data['CellCoords'] = cellCoords
    for row, datapoint in enumerate(xyz_data['CellCoords']):
        for ci, coord in enumerate(datapoint):
            #Clean up first
            #Coords for cell vertices shouldn't be above or below the min/max of the data points per sounding 
            if coord[1] > xyz_data.loc[row, 'SoundingMax']:
                xyz_data.loc[row, 'CellCoords'][ci][1] = xyz_data.loc[row, 'SoundingMax']
            if coord[1] < xyz_data.loc[row, 'SoundingMin']:
                xyz_data.loc[row, 'CellCoords'][ci][1] = xyz_data.loc[row, 'SoundingMin']

            #Coords for cell vertices shouldn't be above the min/max bounding box of data points
            if coord[0] > max_dim0:
                if clean_type=='move':
                    xyz_data.loc[row, 'CellCoords'][ci][0] = max_dim0
                else:
                    xyz_data.loc[row, 'CellCoords'] = pd.NA    
                    break

            if coord[1] > max_dim1:
                if clean_type=='move':
                    xyz_data.loc[row, 'CellCoords'][ci][1] = max_dim1
                else:
                    xyz_data.loc[row, 'CellCoords'] = pd.NA    
                    break

            if coord[0] < min_dim0:
                if clean_type=='move':
                    xyz_data.loc[row, 'CellCoords'][ci][0] = min_dim0
                else:
                    xyz_data.loc[row, 'CellCoords'] = pd.NA    
                    break

            if coord[1] < min_dim1:
                if clean_type=='move':
                    xyz_data.loc[row, 'CellCoords'][ci][1] = min_dim1
                else:
                    xyz_data.loc[row, 'CellCoords'] = pd.NA   
                    break

            #Add the unused dimension coordinate back in so it is in 3D
            for i, dim in enumerate(unusedDim):
                key = list(dim.keys())[0]
                values = dim[key]
                insertIndex = indDict[key]
                xyz_data.loc[row, 'CellCoords'][ci] = list(xyz_data.loc[row, 'CellCoords'][ci])
                xyz_data.loc[row, 'CellCoords'][ci] = np.insert(xyz_data.loc[row, 'CellCoords'][ci], insertIndex, dim[key][row])
    xyz_data.dropna(inplace=True, axis=0, subset='CellCoords')
    xyz_data.reset_index(inplace=True, drop=True)

    #Separate out the lists of coordinates, for plotting purposes primarily
    xyz_data['CellCoords_SepDims'] = xyz_data['CellCoords'].apply(lambda x: [list(t) for t in zip(*x)])

    if plot_vor:
        fig, ax = matplotlib.pyplot.subplots(1)
        for coords in xyz_data['CellCoords_SepDims']:
            ax.plot(coords[0], coords[2])

    return xyz_data