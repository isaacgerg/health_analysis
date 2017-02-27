import datetime
import collections
import seaborn as sns
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas

from statsmodels.formula.api import ols

#---------------------------------------------------------------------------------------------------
def plotCorr(df, title='', corr_type=''):
    if True:     
        a = sp.cluster.hierarchy.fclusterdata(df.values.T, 0.5)
        a = np.argsort(a)
        
        #import matplotlib as mpl
        #mpl.rcParams.update(mpl.rcParamsDefault)    
        
        df = df[a]
        
        corr = df.corr()
        
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True        
        
        sns.heatmap(corr, vmin=-1, vmax=1, center=0, annot=True, linewidths=0.5, mask=mask)
        plt.yticks(rotation = 0)
        plt.xticks(rotation = 'vertical')


    


    return

#---------------------------------------------------------------------------------------------------
BmEntry = collections.namedtuple('BmEntry', 'datetime, type, duration, note')
#---------------------------------------------------------------------------------------------------
def readBowelMoveFile(fn):
    fid = open(fn,'r')
    l = fid.readline().rstrip()
    
    # TODO turn this into regex

    # First line should be entries
    if l != '[ENTRIES]':
        raise('bad file')
        
    while True:
        l = fid.readline().rstrip()
        if len(l) > 0: break
    
    entries = []
    
    # Read until you have text
    done = False
    while not done:        
        # Read entry lines
        time = l
        bType = fid.readline().rstrip()
        duration = fid.readline().rstrip()
        note = fid.readline().rstrip()  # Optional
        
        # Parse date
        time = time[6:23]
        pm = True if time[16] == 'p' else False
        dTime = datetime.datetime(int(time[0:4]), int(time[5:7]), int(time[8:10]), int(time[11:13])+12 if pm and time[11:13] != '12' else int(time[11:13]), int(time[14:16]))
        # Parse bType
        bType = int(bType[6])
        # Parse duration
        # TODO
        
        # Create entry
        entry = BmEntry(dTime, bType, 0, note)
        entries.append(entry)
        
        while True:
            l = fid.readline()
            if len(l) == 0: done = True; break
            if l[0:4] == 'Time': break
                    
    return entries

def regression(eqn, df):
    title = '==================== {0} ===================='.format(eqn)
    titleLen = len(title)
    print('='*titleLen)
    print(title)
    print('='*titleLen)
    model = ols(eqn, df).fit()  
    print(model.summary())
    print('\n\n\n')