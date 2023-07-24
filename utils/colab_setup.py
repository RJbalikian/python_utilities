
#Code to help setup environment in Google Colab
def setup_colab(option='', repo_dir=''):
    """Function to help set up Google Colab environment for SPRIT
    
    This is designed to be run twice in a Google Colab environment without any parameters, and at the beginning of the Google Colab notebook. 
    The first run will install obspy (which is not installed on Colab by default), then restart the kernel (necessary for Colab to run obspy effectively).
    The second run will "install" the repository. 
    
    This will be changed dramatically once the repository is ready for distrubution via pypi.
    
    Parameters
    ----------
    option : str, default=''
        Which iteration to run of setup_colab. Be default, this function can determine which "iteration" it needs to run, but it can be specified manually.
    repo_dir : str or pathlib.Path, default=''
        Where the repository has been "installed"/extracted in the Colab folder structure.
        
    Returns
    -------
    None

    """
    import datetime
    import math
    import os
    import pathlib
    import time
    import sys
    import subprocess

    import matplotlib.pyplot as plt
    import numpy as np
    import scipy

    from google.colab import files
    from zipfile import ZipFile
    #%matplotlib #Run this line if you want interactive plots
    #https://github.com/googlecolab/colabtools/blob/main/google/colab/_system_commands.py
    from google.colab import _system_commands
    pyvers = _system_commands._run_command('python --version', False)
    pyvers = pyvers.output.split(' ')#+pyvers.output.split('.')[1]
    pyvers = pyvers[0].lower()+pyvers[1].split('.')[0]+'.'+pyvers[1].split('.')[1]

    #Setup matplotlib too?
    #_system_commands._run_command('matplotlib qt', False)

    packPath = '/usr/local/lib/'+pyvers+'/dist-packages'
    packPath = pathlib.Path(packPath)
    
    #Make directories
    dataDir = '/content/Data/'
    outputDir = '/content/Output'
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)    
    
    obspyInstalled=False
    for f in packPath.iterdir():
        if 'obspy' in f.name:
            obspyInstalled=True
            global obspy
            import obspy
            break
        
    if 'obspy' in option or option=='':
        if not obspyInstalled:
            print('Installing Obspy')
            _system_commands._run_command('pip install obspy', False)
            print("Runtime will now be reset to properly load obspy")
            print('Please run setup_colab() to upload data and enter code environment.')
            os.kill(os.getpid(), 9)
        else:
            global obspy
            import obspy
            print('Obspy has been imported.') 
    elif 'data' in option:
        global obspy
        import obspy
        print('Obspy has been installed imported.')

        os.chdir(dataDir)
        print('\nUpload data file(s): \n(file(s) will be placed in '+dataDir+')')
        files.upload() #Upload the 3 data files to be used
        if repo_dir == '':
            repo_dir='/content/SPRIT'
        os.chdir(repo_dir)
    return
