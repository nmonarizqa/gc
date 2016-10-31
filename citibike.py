'''
    File name: citibike.py
    Author: Nurvirta Monarizqa
    Date created: 10/30/2016
    Python Version: 2.7
'''

from zipfile import ZipFile
from StringIO import StringIO
import urllib2
import pandas as pd
from geopy.distance import great_circle

def main():
    data = get_data()
    result = []
    result.append(get_median_duration(data),\
                get_fraction_zero_distance(data),\
                get_std_station(data),\
                get_avg_distance(data),\
                get_short_long_monthly_diff(data),\
                get_largest_hourly_ratio(data),\
                get_exceed_limit_frac(data),\
                get_avg_moved_times(data)]

    for i in len(result):
        print "Q "+str(i+1)+" answer: " + str(result[i])

def getdata():
    months = ["{:02d}".format(x+1) for x in range(12)]
    data = pd.DataFrame()
    for month in months:
        base = 'https://s3.amazonaws.com/tripdata/2015'
        r = urllib2.urlopen(base + month +'-citibike-tripdata.zip').read()
        z = ZipFile(StringIO(r))
        citibikedata = z.open('2015'+month+'-citibike-tripdata.csv')
        data = pd.concat([data,pd.read_csv(citibikedata)])

        # convert Date
        A = data[(key=='1/') | (key=='2/') | (key=='3/')| (key=='6/')].copy()
        B = data[(key!='1/') & (key!='2/') & (key!='3/') & (key!='6/')].copy()
        A['date'] = pd.to_datetime(A['starttime'],format='%m/%d/%Y %H:%M')
        B['date'] = pd.to_datetime(B['starttime'],format='%m/%d/%Y %H:%M:%S')
        data = pd.concat([A,B])
        return data

def get_median_duration(data):
    return data['tripduration'].median()

def get_fraction_zero_distance(data):
    data['start-stop'] = data['start station id'] - data['end station id']
    same_station = len(data[data['start-stop']==0])
    return same_station/len(data)

def get_std_station(data):
    startlist = data.groupby('bikeid')['start station id'].apply(list)
    stoplist = data.groupby('bikeid')['end station id'].apply(list)
    stationlist = startlist + stoplist
    visited_station = []
    for i in range(len(stationlist)):
        unique_station = len(np.unique(stationlist.iloc[i]))
        visited_station.append(unique_station)
    return np.std(visited_station)

def get_short_long_monthly_diff(data):
    data['month'] = data['date'].dt.month
    duration_per_month = data.groupby('month').mean()['tripduration']
    return max(duration_per_month) - min(duration_per_month)

def get_exceed_limit_frac(data):
    exceedcust = len([x for x in byusertype['Customer'] if x> 1800])
    exceedsubs = len([x for x in byusertype['Subscriber'] if x> 2700])
    return float(exceedcust + exceedsubs)/float(len(data))

def getdistance(data):
    return great_circle(df['start location'],df['stop location']).km

def get_avg_distance(data):
    data['start location'] = data['start station latitude'].map(str) + ',' \
                            + data['start station longitude'].map(str)
    data['stop location'] = data['end station latitude'].map(str) + ',' \
                            + data['end station longitude'].map(str)
    data['route'] = data['start location'] + ','+ data['stop location']
    routemap = data[['start location','stop location','route']].drop_duplicates('route').copy()
    routemap['distance'] = routemap.apply(getdistance,axis=1)
    data = pd.merge(data,routemap,how='left',on='route')
    return data.distance[data.distance>0].mean()

def get_largest_hourly_ratio(data):
    hourly = data.groupby(['hour','start station id']).count()['tripduration']
    hourly = hourly.reset_index()
    hpivot = hourly.pivot_table(index='start station id', \
                            columns='hour',values='tripduration')
    hpivottotal = hpivot.sum(axis=1)
    hpivot_frac = hpivot.div(hpivottotal,axis=0)
    hourly_all = data.groupby(['hour']).count()['tripduration']
    hourly_all_frac = hourly_all/hourly_all.sum()
    frac = hpivot_frac.div(hourly_all_frac,axis=1)
    return frac.max(axis=1).max()

def get_avg_moved_times(data):
    data=data.sort_values('date',ascending=True)
    startlist = data.groupby('bikeid')['start station id'].apply(list)
    stoplist = data.groupby('bikeid')['end station id'].apply(list)

    moved = []
    for i in range(len(startlist)):
        journey = pd.DataFrame({'start':startlist.iloc[i]+[0],
                            'stop':[0]+stoplist.iloc[i]})
        journey['sel']=journey.start-journey.stop
        moved.append(len(journey[journey.sel!=0])-2)
    return np.mean(moved)

if __name__ == '__main__':
    main()
