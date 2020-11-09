import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def get_gpats_data(cur_dir:str="./gpats_data/",sta:str="YBBN",res=None)->pd.DataFrame:
    """[summary]
    Args:
        cur_dir (str, optional): [Folder that stores gpat data]. Defaults to "./gpats_data/".

        sta (str, optional): [Aviation ID/location]. Defaults to "YBBN".

        res (str): downsample bin size
        The gpats data is micro sec resolution. Thats a lot of data points and huge memory gobbler!
        a resample to 1min will downsample the series into 1 minute bins and sum the values of the timestamps falling into a bin
        a resample to 30min likewise downsamples to into 30 minute bins, H - 1hour bins, D - 1day into daily bins, M in monthly etc etc
        resample takes these other optional parameters, 'closed' and 'label'

        closed : {‘right’, ‘left’}
        For downsampling, set to ‘left’ or ‘right’ to specify which side/end of the interval is closed. 
        The default is ‘left’ for all frequency offsets except for ‘M’, ‘A’, ‘Q’, ‘BM’, ‘BA’, ‘BQ’, 
        and ‘W’ which all have a default of ‘right’.

        label : {‘right’, ‘left’}
        Which bin edge label to label bucket with.
        specifies whether the result is labeled with the beginning or the end of the interval.
        The default is ‘left’ for all frequency offsets except for ‘M’, ‘A’, ‘Q’, ‘BM’, ‘BA’, ‘BQ’, 
        and ‘W’ which all have a default of ‘right’.

        ideally you want to resample to 1min if you want to merge with aws METAR/SPECI data

    Returns:
        pd.DataFrame: [description]
    """
    # join is smart so cur_dir can be like ./gpats  or ./gpats/
    gpats_file = os.path.join(cur_dir, f'gpats_{sta.upper()}_10NM.csv')
    print("Reading {} gpats file {}".format(sta, gpats_file))
    if res is None:
        return (pd.read_csv(gpats_file,parse_dates=True, index_col='TM'))
    else:
        return(pd.read_csv(gpats_file,parse_dates=True, index_col='TM').\
                resample(res).\
                agg(dict(LATITUDE='mean', LONGITUDE='mean', AMP='count')).\
                dropna())


# def get_gpats_start_end_duration(cur_dir:str="./gpats_data/",sta:str="YBBN",res=None)->pd.DataFrame:
def get_gpats_start_end_duration(gpat:pd.DataFrame)->pd.DataFrame:
    """[function loads 10nm gpats data for station (already downsample to 1minute bins)
    and finds daily aggregates for ts start time, end time, duration and total gpats counts

    Args:
        gpat (pd.DataFrame): [gpats data downsampled to 1min bins,closed to left, no NaNs]

    Returns:
        pd.DataFrame: [ gpats_cnt: int64 ('AMP' column for counting strikes)
                        duration : timedelta64[ns] (just timedelta last - first)
                        first    : datetime64[ns] (uses 'Time' col first and last gpats for a given day)
                        last     : datetime64[ns]]
    """

    gpats = gpat.copy()
    # create column needed for time aggregates, first and last gpats strike for given day
    gpats['time'] = gpats.index

    ''' resample data to daily
    - count number of gpats strikes on day in new column 'gpats_cnt'
    - first gpats strike on day in new column 'first'
    - last  gpats strike on day in new column 'last'
    dropna() again as resample('D') would introduce new intermediate days when no lightning recorded
    '''
    # columns ['LATITUDE', 'LONGITUDE', 'AMP', 'time']
    gpats = gpats.resample('D')['AMP', 'time']\
                .agg(
                first=('time', 'first'),
                last=('time', 'last'),
                gpats_cnt=('AMP', 'count'),
                ).dropna()
    # gpats['duration'] = round((gpats['last'] - gpats['first'])/np.timedelta64(1, 'h') , 1)
    gpats['duration'] = gpats['last'] - gpats['first']
    gpats = gpats[gpats['duration'] > pd.Timedelta(minutes=1)]

    return( gpats[['gpats_cnt','duration','first','last']])


dict_mon = dict(zip(
    [1,2,3,4,5,6,7,8,9,10,11,12],
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))

map_half_hour = dict(zip(list(range(0, 48,1)),\
                        gpats_by_half_hour.index.strftime('%H%M')))

'''
Monthly thunder days  for aerodrome location
'''

for sta in ['YSSY','YSRI','YWLM','YSCN','YSBK','YSHW','YSHL']:
    gpats_file = os.path.join(cur_dir, f'gpats_{sta}_10NM.csv')
    dat = get_gpats_data(cur_dir=cur_dir,sta=sta,res='H')['AMP'].resample('D').count()
    # ts_days = dat.loc[dat>0]
    ts_days = dat.loc[dat>1]  # if we demand more than one gpats strikes on given day !
    avg_mon_ts_days = ts_days.groupby(ts_days.index.month).count()/12


    fig, ax = plt.subplots(figsize=(10,5), nrows=1, ncols=1 )
    avg_mon_ts_days.plot( kind='bar', ax=ax)
    title = f'Average Monthly Thunder days at {sta}:\
    {ts_days.index[0].strftime("%b-%Y")} to {ts_days.index[-1].strftime("%b-%Y")}'
    ax.set_title(title, color='b',fontsize=15)
    ax.set_ylabel('Num of Days', color='g', fontsize=15)
    ax.set_xlabel('Month', color='g', fontsize=15)

    dict_mon = dict(zip(
    [1,2,3,4,5,6,7,8,9,10,11,12],
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))
    xlabels=[dict_mon[x+1] for x in ax.get_xticks()]
    ax.set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    ax.tick_params(labelsize=10)
    plt.savefig(f'./ts_plots/{sta}_Average_Thunder_days_month.eps', format='eps', dpi=1000)
    # plt.savefig(f'./ts_plots/{sta}_Average_Thunder_days_month.png', format='png', dpi=300)


'''
Storm frequency by time of day half hourly
'''
for sta in ['YSSY','YSRI','YWLM','YSCN','YSBK','YSHW','YSHL']:

    # print(f"Processing station = {sta}")
    g1_half_hour =  get_gpats_data(cur_dir=cur_dir,sta=sta,res='30T')  #30min bins for 1/2 hr bin intervals
    # we get max 1 gpats count for any 30min period , so its either 0 or 1 for every 30 minute
    # giving max gpats count 2 in an hour
    g1_half_hour = g1_half_hour.loc[g1_half_hour['AMP']>1]

    #gpats_by_hour = g1_hour.groupby(g1_hour.index.hour).count()
    # getting half hourly freq/counts is not so simple
    # 1st create colum with HH:MM and use that for aggregation
    g1_half_hour['Time'] = pd.to_datetime(g1_half_hour.index.strftime('%H:%M'))
    gpats_by_half_hour = g1_half_hour.groupby(pd.Grouper(key='Time',freq='30T'))['AMP'].count()

    fig, ax = plt.subplots(figsize=(10,5), nrows=1, ncols=1 )
    gpats_by_half_hour.plot( kind='bar', ax=ax)
    title = f'TS at {sta} (all seasons {g1_half_hour.index[0].strftime("%b-%Y")} to {g1_half_hour.index[-1].strftime("%b-%Y")})'
    ax.set_title(title, color='b',fontsize=15)
    ax.set_ylabel('Frequency', color='g', fontsize=15)
    ax.set_xlabel('Time of day UTC ', color='g', fontsize=15)
    # g.get_xticks() [ 0  1  2  3  4  5  6  7  8  9 10]

    # get half hour tick mark labels, 48 half hourly steps
    map_half_hour = dict(zip(list(range(0, 48,1)),gpats_by_half_hour.index.strftime('%H%M')))
    # drop the half hour lables, keep houly labels only
    xlabels=[map_half_hour[x] if x%2==0 else '' for x in ax.get_xticks() ])]
    ax.set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    #g.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.tick_params(labelsize=8)
    plt.savefig(f'./ts_plots/{sta}_TS_by_halfhour.eps', format='eps', dpi=1000)
    # plt.savefig(f'ts_plots_{sta}_TS_by_halfhour.png', format='png', dpi=300)


'''
Storm frequency by time of day for individual months
'''

dict_mon = dict(zip(
    [1,2,3,4,5,6,7,8,9,10,11,12],
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))
keys = list(dict_mon.keys())  # 1,2,3,....
vals = list(dict_mon.values())  # 'Jan', 'Feb',,,,


sta='YSSY'
for month in list(dict_mon.values()):
    mon=keys[vals.index(month)]  # get the dict key/index from dict values
    # print(mon)
    # print(f"Processing station = {sta}")
    g1_half_hour =  get_gpats_data(cur_dir=cur_dir,sta=sta,res='30T')  #30min bins for 1/2 hr bin intervals
    g1_half_hour = g1_half_hour.loc[g1_half_hour['AMP']>1]
    # filter data for required month
    g1_half_hour = g1_half_hour.loc[g1_half_hour.index.month==mon]
    # perform half hourly aggregates
    g1_half_hour['Time'] = pd.to_datetime(g1_half_hour.index.strftime('%H:%M'))
    gpats_by_half_hour = g1_half_hour.groupby(pd.Grouper(key='Time',freq='30T'))['AMP'].count()

    fig, ax = plt.subplots(figsize=(10,5), nrows=1, ncols=1 )
    gpats_by_half_hour.plot( kind='bar', ax=ax)
    title = f'TS by time of day at {sta} for {dict_mon[mon]} (all seasons {g1_half_hour.index[0].strftime("%b-%Y")} to {g1_half_hour.index[-1].strftime("%b-%Y")})'
    ax.set_title(title, color='b',fontsize=15)
    ax.set_ylabel('Frequency', color='g', fontsize=15)
    ax.set_xlabel('Time of day UTC ', color='g', fontsize=15)

    xlabels=[map_half_hour[x] for x in ax.get_xticks()]
    # xlabels = ['{:,.2f}'.format(x) + 'K' for x in ax.get_xticks()/1000]
    ax.set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    ax.tick_params(labelsize=9)
    plt.savefig(f'./ts_plots/{sta}_TS_by_hour.eps', format='eps', dpi=1000)
    #plt.savefig(f'./ts_plots/{sta}_TS_by_hour.png', format='png', dpi=300)


# to see hourly variation by season
# TODO Similar do variation by time of day and month on one figure

for sta in ['YSSY','YSRI','YWLM','YSCN','YSBK','YSHW','YSHL']:

    # print(f"Processing station = {sta}")
    g1_hour =  get_gpats_data(cur_dir=cur_dir,sta=sta,res='H')['AMP']  #1hr bin intervals
    # we get max 1 gpats count for any 30min period , so its either 0 or 1 for every 30 minute
    # giving max gpats count 2 in an hour
    g1_hour = g1_hour.loc[g1_hour>1]

    print(g1_hour.head())
    spring = g1_hour.index.month.isin([9,10,11])
    summer = g1_hour.index.month.isin([12,1,2])
    autumn = g1_hour.index.month.isin([3,4,5])
    winter = g1_hour.index.month.isin([6,7,8])


    dat = pd.DataFrame()
    g1_summer = g1_hour.loc[summer]
    g1_spring = g1_hour.loc[spring]
    g1_autumn = g1_hour.loc[autumn]
    g1_winter = g1_hour.loc[winter]

    dat['summer'] = (g1_summer.groupby(g1_summer.index.hour).count())/12
    dat['autumn'] = (g1_autumn.groupby(g1_autumn.index.hour).count())/12
    dat['winter'] = (g1_winter.groupby(g1_winter.index.hour).count())/12
    dat['spring'] = (g1_spring.groupby(g1_spring.index.hour).count())/12

    fig, ax = plt.subplots(figsize=(10,5), nrows=1, ncols=1 )
    '''
    (g1_summer.groupby(g1_summer.index.hour).count()/12).plot(kind='line', color='red', linewidth=2,
        marker='h', markerfacecolor='lightgreen', markeredgewidth=2)
    (g1_spring.groupby(g1_spring.index.hour).count()/12).plot(kind='line', color='blue', linewidth=2,
        marker='h', markerfacecolor='lightblue', markeredgewidth=2)
    (g1_autumn.groupby(g1_autumn.index.hour).count()/12).plot(kind='line', color='yellow', linewidth=2,
        marker='h', markerfacecolor='lightgreen', markeredgewidth=2)
    (g1_winter.groupby(g1_winter.index.hour).count()/12).plot(kind='line', color='green', linewidth=2,
        marker='h', markerfacecolor='lightgreen', markeredgewidth=2)
    '''
    dat.plot(kind='line',ax=ax, linewidth=2, marker='h', markeredgewidth=2)
    
    title = f'Relative Freq TS Occurence by Season at {sta}: \
    {g1_hour.index[0].strftime("%b-%Y")} to {g1_hour.index[-1].strftime("%b-%Y")})'
    ax.set_title(title, color='b',fontsize=15)
    ax.set_ylabel('Relative Frequency', color='g', fontsize=20)
    ax.set_xlabel('Time of day UTC ', color='g', fontsize=20)
    plt.savefig(f'./ts_plots/{sta}_TS_by_seasons.eps', format='eps', dpi=1000)


# compare storm frequency for given stations by time of daya nd month

dict_mon = dict(zip(
    [1,2,3,4,5,6,7,8,9,10,11,12],
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))
keys = list(dict_mon.keys())
vals = list(dict_mon.values())
print(keys)
print(vals)

for sta in ['YSSY']:#,'YSRI','YWLM','YSCN','YSBK','YSHW','YSHL']:

    print(f"Processing station = {sta}")
    g1_half_hour =  get_gpats_data(cur_dir=cur_dir,sta=sta,res='30T')  #1hr bin intervals
    g1_half_hour = g1_half_hour.loc[g1_half_hour['AMP']>1]
    print(g1_half_hour.head())
    print(g1_half_hour.info())

    dat = pd.DataFrame()
    for month in list(dict_mon.values()):
        mon=keys[vals.index(month)]
        print(mon) 
        g = g1_half_hour.loc[g1_half_hour.index.month==mon]
        g['Time'] = pd.to_datetime(g.index.strftime('%H:%M'))
        gpats_by_half_hour = g.groupby(pd.Grouper(key='Time',freq='30T'))['AMP'].count()

        dat[month] = gpats_by_half_hour

    dat.fillna(0)
    fig, ax = plt.subplots(figsize=(10,5), nrows=1, ncols=1 )
    '''
    (g1_summer.groupby(g1_summer.index.hour).count()/12).plot(kind='line', color='red', linewidth=2,
        marker='h', markerfacecolor='lightgreen', markeredgewidth=2)
    '''
    dat.plot(kind='line',ax=ax, linewidth=1, linestyle='-', marker='.', markeredgewidth=2)

    title = f'Frequency of Storms by time of day and month at {sta}: \
    {g1_hour.index[0].strftime("%b-%Y")} to {g1_hour.index[-1].strftime("%b-%Y")})'
    ax.set_title(title, color='b',fontsize=15)
    ax.set_ylabel('Relative Frequency', color='g', fontsize=20)
    ax.set_xlabel('Time of day UTC ', color='g', fontsize=20)

    # get half hour tick mark labels, 48 half hourly steps
    # map_half_hour = dict(zip(list(range(0, 48,1)),g1_half_hour.index.strftime('%H%M')))
    # drop the half hour lables, keep houly labels only
    # xlabels=[map_half_hour[x] if x%2==0 else '' for x in ax.get_xticks() ]
    ax.set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    #g.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.tick_params(labelsize=8)
    plt.savefig(f'./ts_plots/{sta}_TS_by_halfhour_{mon}.eps', format='eps', dpi=500)
    

def compare_gpats_storm(loc1='YSRI',loc2='YSSY'):
    loc1=loc1.upper()
    loc2=loc2.upper()
    g_loc1 =  get_gpats_data(cur_dir,sta=loc1,res='1min')
    ts_loc1 = get_gpats_start_end_duration(g_loc1)[['first','last']]
    g_loc2 =  get_gpats_data(cur_dir,sta=loc2,res='1min')
    ts_loc2 = get_gpats_start_end_duration(g_loc2)[['first','last']]
    
    # https://www.generacodice.com/en/articolo/247120/Python+timedelta+in+years
    
    num_days = ( pd.to_datetime(g_loc1.index[-1]) - pd.to_datetime(g_loc1.index[0]) ).days
    num_years = num_days/365.25
    
    merged = pd.merge(left=ts_loc1, right=ts_loc2,how = 'inner',on='TM')\
    .rename(columns = {'first_x':loc1+'_start', 'last_x':loc1+'_last',\
                       'first_y':loc2+'_start', 'last_y':loc2+'_last'})
    
    print(f'\n\nIn the period between \
    {g_loc1.index[0].strftime("%d-%b-%Y")} and \
    {g_loc1.index[-1].strftime("%d-%b-%Y")}\n(that is {num_years:.1f} years and {num_days} days \
    \nNum of storm days at {loc1} = {ts_loc1.shape[0]}\nNum of storm days at {loc2} = {ts_loc2.shape[0]}\
    \nNum of days with storm recorded at both locations = {merged.shape[0]}')
    
    # loc2 TS start time after TS at loc1
    ts_loc1_then_loc2 = merged.loc[(merged[loc2+'_start']>merged[loc1+'_start'])]
    
    print(f"\nOut of the {merged.shape[0]} days when we have storms at both {loc1} and {loc2},\
    \n- on about {ts_loc1_then_loc2.shape[0]} days or {ts_loc1_then_loc2.shape[0]/merged.shape[0]*100:.0f}%\
    of days, storms occurred at {loc2} after {loc1}, and")

    # YSSY TS start time after TS at YSRI - most likely TS advected from YSRI to YSSY
    ts_loc2_then_loc1 = merged.loc[(merged[loc1+'_start']>merged[loc2+'_start'])]
    
    print(f"- on about {ts_loc2_then_loc1.shape[0]} days or {ts_loc2_then_loc1.shape[0]/merged.shape[0]*100:.0f}%\
    of days, storms occurred at {loc1} after {loc2}.")
    
    print(f"\nNB:The relative frequencies above account for storms affecting both locations on the same day\n\
    and requirement they affect the downstream location {loc2} after {loc1} - this assumes storms at {loc2}\n\
    have advected from {loc1}. This many not always be the case!!")

    print(f"\nOn average storms develop near upstream location {loc1} about 0{pd.to_datetime(ts_loc1_then_loc2[loc1+'_start']).dt.hour.median():.0f}Z")
    print(f"On average storms advect or develop downstream location {loc2} about  0{pd.to_datetime(ts_loc1_then_loc2[loc2+'_start']).dt.hour.median():.0f}Z")
    
    travel_time = (pd.to_datetime(ts_loc1_then_loc2[loc2+'_start']) - \
                  pd.to_datetime(ts_loc1_then_loc2[loc1+'_start']))#.apply(convert_to_hours)
    
    # print(travel_time)
    
    print(f'\nTravel time storm from {loc1} to {loc2} (25% and 75% percentiles in hours:minutes HH:MM):\
    \nbetween {duration(travel_time.quantile(.25))} to\
    {duration(travel_time.quantile(.75))}') #' with mean of {travel_time.quantile(.5)}.')
    

    return(merged,ts_loc1_then_loc2,ts_loc2_then_loc1)



## Convert time HH:MM format to decimal HH.mm
'''60 minutes make an hour -  each minute is one-sixtieth (1/60) of an hour.
Basis for converting number of minutes into fractions of an hour.
To this for ease of plotting time as floats on y-axis
1/60 = 0.016666666666666666
'''
def conversion(x):
    h,m = x.split(':')
    return (int(h) + int(m)/60)

import seaborn as sns
import numpy as np

'''  problems with plotting native datetime on x-axis
Guess the problme we have is we trying to boxplot time
this involves maths mean, quantiles on datetime objects - think thats where problem lies!!!
import matplotlib.dates as mdates
dates = mdates.date2num(ts_stat['first'])
matplotlib.pyplot.plot_date(dates, values
myFmt = mdates.DateFormatter('%H:%M')
axes[1].xaxis.set_major_formatter(myFmt)
'''

dict_mon = dict(zip(
    [1,2,3,4,5,6,7,8,9,10,11,12],
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))

sns.set_style("whitegrid")
# # for sta in ['YSSY','YSRI','YWLM','YSCN','YSBK','YSHW','YSHL']:
for sta in ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YTWB','YBOK','YBWW']:
    gpats_file = os.path.join(cur_dir, f'gpats_{sta}_10NM.csv')
    fig, axes = plt.subplots(figsize=(14,18) , nrows=4, ncols=1)

    dat = get_gpats_data(cur_dir=cur_dir,sta=sta,res='H')['AMP'].resample('D').count()
    ts_days = dat.loc[dat>1]  # if we demand more than one gpats strikes on given day !
    avg_mon_ts_days = ts_days.groupby(ts_days.index.month).count()/12
    print(f"Annual Average thunder days {sum(avg_mon_ts_days):.2f}")

    avg_mon_ts_days.plot( kind='bar', ax=axes[0])
    title = f'Storm Climatology for {sta}:\
    {ts_days.index[0].strftime("%b-%Y")} to {ts_days.index[-1].strftime("%b-%Y")}'
    axes[0].set_title(title, color='b',fontsize=15)
    axes[0].set_ylabel('Avg Monthly Thunder Days', color='g', fontsize=15)
    axes[0].set_xlabel('', color='g', fontsize=15)


    xlabels=[dict_mon[x+1] for x in axes[0].get_xticks()]
    axes[0].set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    axes[0].tick_params(labelsize=8)

    ############################ plot TS start times ##################
    ts_stat = get_gpats_start_end_duration(  get_gpats_data(cur_dir,sta=sta,res='1min') )
    print(ts_stat.info())
    print(ts_stat)

    # round duration to closest 1hour !!
    ts_stat['duration'] = round((ts_stat['last'] - ts_stat['first'])/np.timedelta64(1, 'h') , 1)

    # convert start and end time to numeric
    ts_stat['first'] =  ts_stat['first'].dt.strftime('%H:%M').apply(conversion)
    ts_stat['last'] =  ts_stat['last'].dt.strftime('%H:%M').apply(conversion)

    sns.boxplot(data=ts_stat, x=ts_stat.index.month, y='first', linewidth=2, ax=axes[1])
    axes[1].set_ylabel('Onset (UTC)', color='g', fontsize=15)

    xlabels=[dict_mon[x+1] for x in axes[1].get_xticks()]
    axes[1].set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    axes[1].tick_params(labelsize=8)
    axes[1].set_xlabel('', color='g', fontsize=15)


    ############################ plot TS end times ##################

    sns.boxplot(data=ts_stat, x=ts_stat.index.month, y='last', linewidth=2, ax=axes[2])
    axes[2].set_ylabel('Finish (UTC)', color='g', fontsize=15)

    xlabels=[dict_mon[x+1] for x in axes[2].get_xticks()]
    axes[2].set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    axes[2].tick_params(labelsize=8)
    axes[2].set_xlabel('', color='g', fontsize=15)


    ############################ plot TS duration ##################


    sns.boxplot(data=ts_stat, x=ts_stat.index.month, y='duration', linewidth=2, ax=axes[3])
    axes[3].set_ylabel('Duration (hours)', color='g', fontsize=15)

    xlabels=[dict_mon[x+1] for x in axes[3].get_xticks()]
    axes[3].set_xticklabels(xlabels,rotation=45, horizontalalignment='right')
    axes[3].tick_params(labelsize=8)
    axes[3].set_xlabel('Month', color='g', fontsize=15)
    
    plt.savefig(f'./ts_plots_seqld/{sta}_TS_stats.eps', format='eps', dpi=1000)
