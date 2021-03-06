import datetime
import collections
import urllib
import json

import numpy as np
import pandas as pd
import matplotlib.style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.style.use('matplotlibrc.txt')

import tools

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Read in health sheet data
spreadsheetFilename = r'data/Health Sheet 2017 - Data.csv'
bmFilename = r'data\bm.txt'
endDate = '2017-08-14'
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

# Start at 2017
df_bm = df_bm['2017-01-02':endDate]

# PLOT: delta between movements
df_bm['deltaHours'] = df_bm.index.to_series().diff()/np.timedelta64(1, 'h')
#a, b = np.histogram(df_bm['deltaHours'].as_matrix()[1:], bins=30, range=(0, 60))
#a = a/a.sum()
plt.figure(1)
#plt.plot(np.linspace(0,60,30), a, marker='X')
plt.hist(df_bm['deltaHours'].as_matrix()[1:], bins=48, range=(0,48), normed=True)
plt.xlim(0,48)
plt.axes().xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(1))
plt.xlabel('Delta [Hours]')
plt.ylabel('Proportion')
plt.title('Normalized Histogram of Time Between Movements\nMean: {0}'.format(df_bm['deltaHours'].mean()))
plt.savefig(r'output\time_between_movements.png')
plt.close('all')

# Compute num hard and loose events
df_bm['loose'] = df_bm['type'] >= 6
df_bm['hard'] = df_bm['type'] <=2

# Week year
#df_bm['year_week'] = df_bm.index.year*52 + df_bm.index.week
for index, row in df_bm.iterrows():
    dt = datetime.date(index.year, index.month, index.day)
    df_bm.loc[index, 'year_week'] = dt - datetime.timedelta(days=dt.weekday()) 

p = df_bm.boxplot('type', 'year_week', whis=np.inf, showfliers=False, showmeans=True)  # whis= np.inf shows whisker, 0 hides them
plt.xticks(rotation='vertical', size='xx-large')
plt.title('Bristol Stool Scale by Week')
plt.suptitle('')
plt.xlabel('Week')
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.ylabel('Bristol Stool Scale')
plt.savefig(r'output\bss_box_whisker.png', bbox='tight')

# Determine number of hard / loose per week
tmp = df_bm['type'].resample('W-MON', label='left').mean()
tmp2 = df_bm[['loose','hard']].resample('W-MON', label='left').sum()
tmp2 = tmp2['2017-01-02':]
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
ax = matplotlib.pyplot.gca()
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
plt.xticks(rotation='vertical')
plt.savefig(r'output\bss_mean.png', bbox='tight')

plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.title('Number Abnormal Stools Per Week By Type')
plt.bar(tmp2.index, tmp2['loose'], color='C1', width=4)
plt.bar(tmp2.index, tmp2['hard'], color='C2', width=4, bottom=tmp2['loose'])
plt.ylabel('Count')
plt.xlabel('Week')
plt.legend(['loose','hard'])
plt.xticks(rotation='vertical')
ax = matplotlib.pyplot.gca()
lbls = []
#for k in tmp2.index:
#    lbls.append(k.strftime('%Y-%m-%d'))
#ax.set_xticklabels(lbls)
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.set_xlim(tmp2.index[0], tmp2.index[-1])
plt.savefig(r'output\abnormal.png',  bbox='tight')

plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(8,8)
count  = df_bm['type'].resample('M', label='right').count()
numLoose  = df_bm['loose'].resample('M', label='right').sum()
numHard  = df_bm['hard'].resample('M', label='right').sum()
for c,l,h,label in zip(count, numLoose, numHard, count.index):
    plt.plot(l/c,h/c, 'x')
    plt.annotate(label.strftime('%Y-%m'), xy = (l/c,h/c), xytext = (5,0), textcoords = 'offset points')
plt.xlim(0,1)
plt.ylim(0,1)
plt.xlabel('Proportion Loose Stool')
plt.ylabel('Proportion Hard Stool')
plt.title('Proportion of Abnormal Stool by Month')
plt.plot([0,0.25], [0.25,0], color='black', linestyle='-')
plt.savefig(r'output\abnormal - proportion.png',  bbox='tight')

plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
v = np.array(df_bm['type'])
h = np.histogram(v, bins=7)[0]
h = h/h.sum()
plt.bar(np.arange(1,8), h)
plt.title('Bristol Stool Score Proportions')
plt.xlabel('Score')
plt.ylabel('Proportion')
plt.savefig(r'output\bss - histogram.png',  bbox='tight')

# BSS by day of week
df_bm['weekday'] = df_bm.index.weekday
plt.figure(); 
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)    
p = df_bm.boxplot('type', 'weekday', whis=np.inf, showfliers=True, showmeans=True)
plt.xticks([1,2,3,4,5,6,7], ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.xlabel('Day of Week')
plt.ylabel('Bristol Stool Scale')
plt.title('Bristol Stool Scale by Day of Week')
plt.suptitle('')
plt.savefig(r'output\bss - day of week.png',  bbox='tight')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Format dataframe for regression analysis bringing in all data
# Bring in BM data
dfBm = pd.concat([df_bm['type'].resample('D', how='mean'), df_bm['loose'].resample('D', how='sum'), df_bm['hard'].resample('D', how='sum')], axis=1)
dfBm['loose'] = dfBm['loose'].fillna(0)
dfBm['hard'] = dfBm['hard'].fillna(0)
dfBm = dfBm.rename(columns={'type':'bss'})

# Bring in health spreadsheet data
dfSpreadsheet = pd.read_csv(spreadsheetFilename)
dfSpreadsheet = dfSpreadsheet.ix[:,['Date', 'mean', 'cardio', 'nexium', 'librax', 'weights', 'clrtn', 'vit d [IU]', 'mtmcl', 'AM', 'PM', 'symptoms', 'prilo']]
dfSpreadsheet['Date'] = pd.to_datetime(dfSpreadsheet['Date'])
dfSpreadsheet = dfSpreadsheet.set_index('Date')

# Cleanup
#Remove last day 
dfSpreadsheet = dfSpreadsheet['2017-01-03':endDate]
#dfSpreadsheet = dfSpreadsheet[:(datetime.datetime.now()-datetime.timedelta(days=14)).strftime('%Y-%m-%d')]

# TODO Add wx
#dfSpreadsheet['muTemp'] = 0
#for ki, k in enumerate(dfSpreadsheet.index):    
#    response = urllib.request.urlopen(r'http://api.wunderground.com/api/90949a6393a8eacd/history_{0}/q/PA/State_College.json'.format(k.strftime('%Y%m%d')))
#    data = response.read().decode('utf-8')
#    jdict = json.loads(data)
#    dfSpreadsheet[k]['muTemp'] = jdict['history']['dailysummary'][0]['meantempi']
    
# Cleanup
# Deal wtih div/0 errors
# rename columns
dfSpreadsheet = dfSpreadsheet.rename(columns={'mean': 'hqi'})
dfSpreadsheet = dfSpreadsheet.rename(columns={'vit d [IU]': 'vitd'})
dfSpreadsheet = dfSpreadsheet.rename(columns={'AM': 'hqi_am'})
dfSpreadsheet = dfSpreadsheet.rename(columns={'PM': 'hqi_pm'})
# change datatypes
dfSpreadsheet['hqi'] = dfSpreadsheet['hqi'].astype('float')
dfSpreadsheet['nexium'] = dfSpreadsheet['nexium'].astype('float') / 20 # convert to 20mg doses
# fill in nans
dfSpreadsheet['cardio'] = dfSpreadsheet['cardio'].fillna(0)/60 # convert to hours
dfSpreadsheet['weights'] = dfSpreadsheet['weights'].fillna(0)
dfSpreadsheet['clrtn'] = dfSpreadsheet['clrtn'].fillna(0)
dfSpreadsheet['nexium'] = dfSpreadsheet['nexium'].fillna(0)
dfSpreadsheet['librax'] = dfSpreadsheet['librax'].fillna(0)
dfSpreadsheet['mtmcl'] = dfSpreadsheet['mtmcl'].fillna(0)
dfSpreadsheet['vitd'] = dfSpreadsheet['vitd'].fillna(0)/1000 # make a sane number so matricies for inverseion well conditioned

# master string
allSymptoms = ''
for k in dfSpreadsheet['symptoms']:
    cleaned = str(k)
    cleaned = cleaned.replace(',', ' ')
    allSymptoms += ' ' + cleaned
uniqueSymptoms = allSymptoms.split()
# remove commas
unique = list(set(uniqueSymptoms))
counts = []
for k in unique:
    counts.append(allSymptoms.count(k))

k = np.argsort(counts)
sortCounts = np.sort(counts)             
    
s = [unique[x] for x in k]
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Merge dfSpreadsheet with dfBm
df = pd.merge(dfBm, dfSpreadsheet, how='inner', left_index=True, right_index=True)

for index, row in df.iterrows():
    dt = datetime.date(index.year, index.month, index.day)
    df.loc[index, 'year_week'] = dt - datetime.timedelta(days=dt.weekday()) 


# plot correlation
plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
tools.plotCorr(df[['cardio', 'nexium', 'librax', 'clrtn', 'mtmcl']])
plt.title('Correlation')
plt.savefig(r'output\correlation.png')

# impute missing bss
df['bss'] = df['bss'].interpolate()

# total abnormal events
df['bss_abnormal_events'] = df['loose'] + df['hard']

# Compute moving averages
# NOTE you cannot use minus signs in the name of columns!!!!!!!!!
df['hqi_3daymean'] = df['hqi'].rolling(window=3).mean()
df['hqi_3daymean'] = df['hqi_3daymean'].shift(-3)

df['hqi_7daymean'] = df['hqi'].rolling(window=7).mean()
df['hqi_7daymean'] = df['hqi_7daymean'].shift(-7)

df['hqi_am_3daymean'] = df['hqi_am'].rolling(window=3).mean()
df['hqi_am_3daymean'] = df['hqi_am_3daymean'].shift(-3)

df['hqi_am_7daymean'] = df['hqi_am'].rolling(window=7).mean()
df['hqi_am_7daymean'] = df['hqi_am_7daymean'].shift(-7)

# Straight predictions 3 and 7 days out
df['hqi_3daysout'] = df['hqi'].shift(-3)
df['hqi_7daysout'] = df['hqi'].shift(-7)

# Perform regression
eqn = 'hqi_3daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)
    
eqn = 'hqi_7daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'hqi_am_3daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'hqi_am_7daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'hqi_3daysout ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)
eqn = 'hqi_7daysout ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

# Compute more moving averages
df['bss_3daymean'] = df['bss'].rolling(window=3).mean()
df['bss_3daymean'] = df['bss_3daymean'].shift(-3)

df['bss_7daymean'] = df['bss'].rolling(window=7).mean()
df['bss_7daymean'] = df['bss_7daymean'].shift(-7)

df['bss_3daysout'] = df['bss'].shift(-3)
df['bss_7daysout'] = df['bss'].shift(-7)

eqn = 'bss_3daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'bss_7daymean ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

# More averaging
df['bss_abnormal_events_3day'] = df['bss_abnormal_events'].rolling(window=3).sum()
df['bss_abnormal_events_3day'] = df['bss_abnormal_events_3day'].shift(-3)

df['bss_abnormal_events_7day'] = df['bss_abnormal_events'].rolling(window=7).sum()
df['bss_abnormal_events_7day'] = df['bss_abnormal_events_7day'].shift(-7)

eqn = 'bss_abnormal_events_3day ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'bss_abnormal_events_7day ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)

eqn = 'bss_3daysout ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)
eqn = 'bss_7daysout ~ cardio + nexium + librax + clrtn + vitd + mtmcl'
tools.regression(eqn, df)


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Mean HQI while on each medicine
# TODO graph these via box and whisker
prilo = df[['hqi', 'prilo']].dropna()
prilo.mean()
nexium = df[['hqi', 'nexium']].dropna()
nexium.mean()

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# HQI plots
tmp = df['hqi'].resample('W-MON', label='left').mean()
plt.figure()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.plot(tmp.index, tmp, color='C0', marker='X')
plt.title('Mean HQI Per Week')
plt.ylabel('HQI')
plt.ylim(1,4)
ax = matplotlib.pyplot.gca()
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
plt.xticks(rotation='vertical')
plt.savefig(r'output\hqi.png',  bbox='tight')

# Meds
for k in ['nexium', 'librax', 'clrtn', 'vitd', 'prilo']:
    plt.figure()
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(16,9)
    tmp = df[k].resample('W-MON', label='left').mean()
    plt.plot(tmp, marker='X');
    #plt.ylim(0,8)
    plt.ylabel('Dose')
    plt.xlabel('Week')
    plt.title('{0} Dose Mean Per Week'.format(k))
    ax = matplotlib.pyplot.gca()
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    plt.xticks(rotation='vertical')
    plt.savefig(r'output\{0}_mean.png'.format(k), bbox='tight')
    plt.close('all')

p = df.boxplot('hqi', 'year_week', whis=np.inf, showfliers=True, showmeans=True)
plt.ylim(1,4)
plt.xticks(rotation='vertical', size='xx-large')
plt.title('Health Quality Index by Week')
plt.suptitle('')
plt.xlabel('Week')
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.ylabel('Health Quality Index')
plt.savefig(r'output\hqi_box.png', bbox='tight')

df_cardio = df[['cardio', 'year_week']]
df_cardio['cardio'] *= 60
p = df_cardio.boxplot('cardio', 'year_week', whis=np.inf, showfliers=True, showmeans=True)
mx = df_cardio['cardio'].max()
ticks = np.arange(0,30*(np.ceil(mx/30)+1),30)
plt.yticks(ticks)
plt.ylim(0,None)
plt.xticks(rotation='vertical', size='xx-large')
plt.title('Cardiovascular Exercise by Week')
plt.suptitle('')
plt.xlabel('Week')
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)
plt.ylabel('Minutes per Day')
plt.savefig(r'output\cardio_box.png', bbox='tight')

# HQI by day of week
df['weekday'] = df.index.weekday
plt.figure(); 
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(16,9)    
p = df.boxplot('hqi', 'weekday', whis=np.inf, showfliers=True, showmeans=True)
plt.xticks([1,2,3,4,5,6,7], ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.xlabel('Day of Week')
plt.ylabel('HQI')
plt.title('Health Quality Index (HQI) by Day of Week')
plt.suptitle('')
plt.ylim([1,4])
plt.savefig(r'output\hqi - day of week.png',  bbox='tight')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
print('Done')