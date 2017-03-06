import datetime
import collections

import numpy as np
import pandas as pd
import matplotlib.style
import matplotlib.pyplot as plt
matplotlib.style.use('seaborn-deep')

import seaborn

#import matplotlib as mpl
#mpl.rcParams.update(mpl.rcParamsDefault)

import tools

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Read in health sheet data
spreadsheetFilename = r'data/Health Sheet 2017 - Data.csv'
bmFilename = r'data\bm.txt'
#-----------------------------------------------------------------------------------------------------------------------------------------------------

# reading in json example
if False:
    file = r'C:\Users\idg101\Desktop\New folder\repo\ubiome_longitudinal_analysis\sample_data\09102016.json' #09102016
    import json
    j = json.load(open(file))
    json.dumps(j['ubiome_bacteriacounts'])
    df = pd.read_json(json.dumps(j['ubiome_bacteriacounts']), orient='records')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Read in BM data
entries = tools.readBowelMoveFile(bmFilename)
bmArray = []
for k in range(len(entries)):
    bmArray.append((pd.Timestamp(entries[k].datetime), entries[k].type))
bmArray.reverse()

# Create dataframe
df_bm = pd.DataFrame.from_records(data = bmArray, columns = ['datetime', 'type'], index='datetime')

# sort
df_bm = df_bm.sort_index()

# PLOT: delta between movements
df_bm['deltaHours'] = df_bm.index.to_series().diff()/np.timedelta64(1, 'h')
a, b = np.histogram(df_bm['deltaHours'].as_matrix()[1:], bins=30, range=(0, 60))
a = a/a.sum()
plt.figure(1)
plt.plot(np.linspace(0,60,30), a, marker='X')
plt.xlabel('Delta [Hours]')
plt.ylabel('Probability')
plt.title('Normalized Histogram of Time Between Movements\nMean: {0}'.format(df_bm['deltaHours'].mean()))
plt.savefig('time_between_movements.png')
plt.close('all')

# Compute num hard and loose events
df_bm['loose'] = df_bm['type'] >= 6
df_bm['hard'] = df_bm['type'] <=2

# Determine number of hard / loose per week
tmp = df_bm['type'].resample('W-MON').mean()
tmp2 = df_bm[['loose','hard']].resample('W-MON').sum()
tmp2['total'] = tmp2['loose'] + tmp2['hard']

# Plot results
plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.plot(tmp, marker='X');
plt.ylim(0,8)
plt.ylabel('Bristol Stool Scale')
plt.xlabel('Week')
plt.title('Bristol Stool Scale Mean Per Week')
plt.axhline(y=3, color='gray', linestyle='--')
plt.axhline(y=5, color='gray', linestyle='--')
plt.savefig('bss_mean.png', bbox='tight')

plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.subplot(2,1,1)
plt.plot(tmp2.index, tmp2['total'], color='C0', marker='X')
plt.title('Total Abnormal Stools Per Week')
plt.ylabel('Count')
plt.subplot(2,1,2)
plt.title('Number Abnormal Stools Per Week By Type')
plt.plot(tmp2.index, tmp2['loose'], color='C1', marker='X')
plt.plot(tmp2.index, tmp2['hard'], color='C2', marker='X')
plt.ylabel('Count')
plt.legend(['loose','hard'])
plt.savefig('abnormal.png',  bbox='tight')


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Format dataframe for regression analysis bringing in all data
# Bring in BM data
dfBm = pd.concat([df_bm['type'].resample('D', how='mean'), df_bm['loose'].resample('D', how='sum'), df_bm['hard'].resample('D', how='sum')], axis=1)
dfBm['loose'] = dfBm['loose'].fillna(0)
dfBm['hard'] = dfBm['hard'].fillna(0)
dfBm = dfBm.rename(columns={'type':'bss'})

# Bring in health spreadsheet data
dfSpreadsheet = pd.read_csv(spreadsheetFilename)
dfSpreadsheet = dfSpreadsheet.ix[:,['Date', 'mean', 'cardio', 'nexium', 'librax', 'weights', 'clrtn']]
dfSpreadsheet['Date'] = pd.to_datetime(dfSpreadsheet['Date'])
dfSpreadsheet = dfSpreadsheet.set_index('Date')
# Cleanup
# Remove last day to deal wtih div/0 errors
dfSpreadsheet = dfSpreadsheet[:(datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
# rename columns
dfSpreadsheet = dfSpreadsheet.rename(columns={'mean': 'hqi'})
# change datatypes
dfSpreadsheet['hqi'] = dfSpreadsheet['hqi'].astype('float')
dfSpreadsheet['nexium'] = dfSpreadsheet['nexium'].astype('float')
# fill in nans
dfSpreadsheet['cardio'] = dfSpreadsheet['cardio'].fillna(0)
dfSpreadsheet['weights'] = dfSpreadsheet['weights'].fillna(0)
dfSpreadsheet['clrtn'] = dfSpreadsheet['clrtn'].fillna(0)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Merge dfSpreadsheet with dfBm
df = pd.merge(dfBm, dfSpreadsheet, how='inner', left_index=True, right_index=True)

# plot correlation
plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
tools.plotCorr(df[['cardio', 'nexium', 'librax']])
plt.title('Correlation')
plt.savefig('correlation.png')

# impute missing bss
df['bss'] = df['bss'].interpolate()

# total adverse events
df['bss_adverse_events'] = df['loose'] + df['hard']

# Compute moving averages
# NOTE you cannot use minus signs in the name of columns!!!!!!!!!
df['hqi_3daymean'] = df['hqi'].rolling(window=3).mean()
df['hqi_3daymean'] = df['hqi_3daymean'].shift(-3)

df['hqi_7daymean'] = df['hqi'].rolling(window=7).mean()
df['hqi_7daymean'] = df['hqi_7daymean'].shift(-7)


# Perform regression
eqn = 'hqi_7daymean ~ cardio + nexium + librax'
tools.regression(eqn, df)
    
eqn = 'hqi_3daymean ~ cardio + nexium + librax'
tools.regression(eqn, df)

eqn = 'hqi_7daymean ~ cardio + nexium + librax'
tools.regression(eqn, df)

# Compute more moving averages
df['bss_3daymean'] = df['bss'].rolling(window=3).mean()
df['bss_3daymean'] = df['bss_3daymean'].shift(-3)

df['bss_7daymean'] = df['bss'].rolling(window=7).mean()
df['bss_7daymean'] = df['bss_7daymean'].shift(-7)

eqn = 'bss_3daymean ~ cardio + nexium + librax'
tools.regression(eqn, df)

eqn = 'bss_7daymean ~ cardio + nexium + librax'
tools.regression(eqn, df)

# More averaging
df['bss_adverse_events_3day'] = df['bss_adverse_events'].rolling(window=3).sum()
df['bss_adverse_events_3day'] = df['bss_adverse_events_3day'].shift(-3)

df['bss_adverse_events_7day'] = df['bss_adverse_events'].rolling(window=7).sum()
df['bss_adverse_events_7day'] = df['bss_adverse_events_7day'].shift(-7)

eqn = 'bss_adverse_events_3day ~ cardio + nexium + librax'
tools.regression(eqn, df)

eqn = 'bss_adverse_events_7day ~ cardio + nexium + librax'
tools.regression(eqn, df)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# HQI plots
tmp = df['hqi'].resample('W-MON').mean()

plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.plot(tmp.index, tmp, color='C0', marker='X')
plt.title('Mean HQI Per Week')
plt.ylabel('HQI')
plt.ylim(1,4)
plt.savefig('hqi.png',  bbox='tight')
#-----------------------------------------------------------------------------------------------------------------------------------------------------
print('Done')