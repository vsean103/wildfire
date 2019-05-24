#!/usr/bin/env python
# coding: utf-8

# # 1- Read MINX data
# MINX parser is in a separate python file: read_minx.py

# In[1]:


import json
import pandas as pd
import math
from pprint import pprint
from datetime import datetime, timedelta
import os
import gzip
from urllib.request import urlretrieve


# In[2]:


PATH = "../data/plume_dataset/plume_test.json"

with open(PATH) as f:
    data = json.load(f)

pprint(data)


# In[3]:


count = len(data)
count


# In[4]:


data[9]


# # 2- Add centroid of fire, based on polygon tables from MINX

# In[5]:


for i in range(count):
    xs = data[i]['polygon']['lon']
    ys = data[i]['polygon']['lat']
    x, y = (sum(xs) / len(xs)), (sum(ys) / len(ys))
    data[i]['centroid_lon'] = round(x,2)
    data[i]['centroid_lat'] = round(y,2)


# In[6]:


print('Lon, Lat')
for i in range(count):
    print(str(data[i]['centroid_lon']) + ', ' + str(data[i]['centroid_lat']))
#     print(data[i]['centroid_lat'])


# # 3- Add underground water from GRACE

# In[7]:


def bilinear_interpolation(x, y, points):
    '''Interpolate (x,y) from values associated with four points.

    The four points are a list of four triplets:  (x, y, value).
    The four points can be in any order.  They should form a rectangle.

        >>> bilinear_interpolation(12, 5.5,
        ...                        [(10, 4, 100),
        ...                         (20, 4, 200),
        ...                         (10, 6, 150),
        ...                         (20, 6, 300)])
        165.0

    '''
    # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation

    points = sorted(points)               # order points by x, then by y
    (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

    if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        raise ValueError('points do not form a rectangle')
    if not x1 <= x <= x2 or not y1 <= y <= y2:
        raise ValueError('(x, y) not within the rectangle')

    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)


# In[8]:


def reverse_convert_to_grace_longitude(x):
    # convert grace longitude 0-360 to -180 to 180
    return x-180

def convert_to_grace_longitude(x):
    return x+180


# In[9]:


def get_grace(df, lon, lat):
    qq = df[(df['LON']==lon) & (df['LAT']==lat)]['GRACE']
    return float(qq)


# In[10]:


# Add GRACE underground water
for i in range(count):
    print(data[i]['date'])


# In[11]:


PATH = "../data/grace_dataset/csv/"

for i in range(count):
    year, month, day = data[i]['date'].split('-')
#     print(year, month, day)
    filename = 'GLDAS_NOAH10_M.A'+str(year)+str(month)+'.totalH2O.txt.csv'
#     print(filename)

    lon = data[i]['centroid_lon']
    lat = data[i]['centroid_lat']
    x1 = round(lon) - 0.5
    x2 = round(lon) + 0.5
    y1 = round(lat) - 0.5
    y2 = round(lat) + 0.5
#     print(x1,y1)
#     print(x2,y2)
    
    x1 = convert_to_grace_longitude(x1)
    x2 = convert_to_grace_longitude(x2)
    lon = convert_to_grace_longitude(lon)

    df = pd.read_csv(PATH+filename)
    q11 = get_grace(df, x1, y1)
    q12 = get_grace(df, x1, y2)
    q21 = get_grace(df, x2, y1)
    q22 = get_grace(df, x2, y2)
    points = [(x1, y1, q11), (x1, y2, q12), (x2, y1, q21), (x2, y2, q22)]
    grace = bilinear_interpolation(lon, lat, points)
    data[i]['grace'] = round(grace,2)
    print(data[i]['grace'])


# # 4- Add NDVI from MODIS

# In[12]:


# read MODIS NDVI

from pyhdf import SD
import numpy as np
# from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
import sys
import h5py
import time
import calendar
from datetime import datetime


# In[13]:


for i in range(count):
    print(data[i]['date'])


# In[14]:


for i in range(count):
    day_of_year = datetime.strptime(data[i]['date'], '%Y-%m-%d').timetuple().tm_yday
    print(data[i]['date'], day_of_year)


# In[15]:


import glob
from pyproj import Proj

p_modis_grid = Proj('+proj=sinu +R=6371007.181 +nadgrids=@null +wktext')


# In[16]:


upper_ul_x = -20015109.354
upper_ul_y = 10007554.677
tile_h = 8
tile_v = 5
pixel_resolution_m = 500
tile_resolution_m = 1200000

def convert_global_xy_to_grid_xy(lon, lat):
    x,y = p_modis_grid(lon, lat)

    im_ul_x = upper_ul_x + tile_h*tile_resolution_m
    im_ul_y = upper_ul_y - tile_v*tile_resolution_m

    im_x = (im_ul_x - x)/pixel_resolution_m
    im_y = (y - im_ul_y)/pixel_resolution_m

    return im_x, im_y


# In[17]:


PATH = "../data/modis_dataset/"
# FILE_NAME = PATH + "MOD13Q1.A2008161.h08v05.006.2015176070634.hdf"
# start_day_of_year = 161
# year = 2008 # data[i]['date']
def get_modis_ndvi(data, day_of_year, year):
    filename = PATH + "*.A"+str(year)+"*"+str(day_of_year)+"*.hdf"
    name = glob.glob(filename)[0]
    # print(name)
    hdf = SD.SD(name)
    # Get the selected dataset
    ndvi = hdf.select('250m 16 days NDVI')
    # get the data
    ndvi = ndvi[:]
    lon, lat = data['centroid_lon'], data['centroid_lat']
    im_x, im_y = convert_global_xy_to_grid_xy(lon, lat)
    x, y = round(im_x), round(im_y)
    return ndvi[x,y]


# In[18]:


for i in range(count):
    day_of_year = datetime.strptime(data[i]['date'], '%Y-%m-%d').timetuple().tm_yday
    year = datetime.strptime(data[i]['date'], '%Y-%m-%d').year
    start = 16 * math.floor(int(day_of_year)/16) + 1
    end = start + 16
    start_ndvi = get_modis_ndvi(data[i], start, year)
    end_ndvi = get_modis_ndvi(data[i], end, year)
    data[i]['ndvi'] = round((start_ndvi+end_ndvi)/2, 2)


# In[19]:


for i in range(count):
    print(data[i]['ndvi'])


# # 5- Add ESI from ESI Tif files
# https://gis1.servirglobal.net/data/esi/4WK/

# In[27]:


from osgeo import osr, ogr
import gdal


# In[28]:


PATH_ESI = "../data/esi_dataset/"

def get_esi(lon, lat, day_of_year, year):
    filename = PATH_ESI+"*"+str(year)+str(day_of_year).zfill(3)+".tif"
    name = glob.glob(filename)[0]
#     print(name)
    esi = gdal.Open(name)
    transform = esi.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = -transform[5]
#     lon, lat = data['centroid_lon'], data['centroid_lat']
    src = osr.SpatialReference()
    src.SetWellKnownGeogCS("WGS84")
    projection = esi.GetProjection()
    dst = osr.SpatialReference(projection)
    ct = osr.CoordinateTransformation(src, dst)
    xy = ct.TransformPoint(lon, lat)
    x = round(((xy[0] - xOrigin) / pixelWidth))
    y = round(((yOrigin - xy[1]) / pixelHeight))
    esi = esi.ReadAsArray()
    return esi[x,y]


# In[29]:


for i in range(count):
    day_of_year = datetime.strptime(data[i]['date'], '%Y-%m-%d').timetuple().tm_yday
    year = datetime.strptime(data[i]['date'], '%Y-%m-%d').year
    lon, lat = data[i]['centroid_lon'], data[i]['centroid_lat']
    start = 7 * math.floor(int(day_of_year)/7) + 1
    end = start if (int(day_of_year) <= 8) else (start+7)
    start_esi = get_esi(lon, lat, start, year)
    end_esi = get_esi(lon, lat, end, year)
    data[i]['esi'] = round((start_esi+end_esi)/2, 2)
    print(data[i]['esi'])


# In[30]:


for i in range(count):
    print(data[i]['centroid_lon'], data[i]['centroid_lat'])


# # 6- Add Temperature and Pressure from ISD data

# ## a. Read CA station information

# In[31]:


STATION_PATH = '../data/isd/isd_station_cali.csv'
df_station = pd.read_csv(STATION_PATH)
df_station.head()


# In[32]:


count_station = len(df_station)
count_station


# In[33]:


# convert column BEGIN & END to datetime
df_station['BEGIN'] = df_station['BEGIN'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
df_station['END'] = df_station['END'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
df_station


# ## b. Add closest weather station to Plume dataset

# In[34]:


# Euclidean distance
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


# In[35]:


for i in range(count):
    plume = (data[i]['centroid_lat'], data[i]['centroid_lon'])
    plume_date = datetime.strptime('{date}-{time}'.format(date=data[i]['date'], time=data[i]['time_UTC']), '%Y-%m-%d-%H:%M:%S')
    index_closest_station = 0
    distance_closest_station = 0
    # filter valid station for less computation and no duplicate stations when they have multiple periods of time
    df_filtered_station = df_station[(df_station['BEGIN']<=plume_date)&(df_station['END']>=plume_date)]
    df_filtered_station = df_filtered_station.reset_index(drop=True) # reset index of the filtered
    if len(df_filtered_station)==0:
        print('No station data for this plume location!')
    else:
        for index, row in df_filtered_station.iterrows():
            station = (row['LAT'], row['LON'])
            dist = distance(plume, station)
            if index==0:
                index_closest_station = 0
                distance_closest_station = dist
            else:
                # if new station is closer
                if dist<distance_closest_station:
                    distance_closest_station = dist
                    index_closest_station = index
        data[i]['distance_closest_station'] = distance_closest_station
        data[i]['USAF'] = df_filtered_station.iloc[index_closest_station]['USAF']
        data[i]['WBAN'] = df_filtered_station.iloc[index_closest_station]['WBAN']
        data[i]['STATION'] = df_filtered_station.iloc[index_closest_station]['STATION NAME']
        data[i]['CTRY'] = df_filtered_station.iloc[index_closest_station]['CTRY']
        data[i]['ST'] = df_filtered_station.iloc[index_closest_station]['ST']    


# In[36]:


for i in range(count):
    print(data[i]['date'], data[i]['distance_closest_station'], data[i]['USAF'], data[i]['WBAN'], data[i]['STATION'], data[i]['CTRY'], data[i]['ST'])


# ## c. Download ISD file for each station

# In[37]:


# unzip file
def unzip(input_file, outputfile):
    input = gzip.GzipFile(input_file, 'rb')
    s = input.read()
    input.close()
    
    output = open(output_file, 'wb')
    output.write(s)
    output.close()
    print("Done unzipping file: "+output_file)
            


# In[38]:


# download & unzip
def download(url_filename, download_file, output_file):
    # check the zip file (.gz)
    existing = os.path.isfile(download_file)
    if not existing:
        try:
            urlretrieve(url_filename, filename=download_file)
            unzip(download_file, output_file)
        except FileNotFoundError:
            print("File not found at: "+url_filename)


# In[41]:


# identifies what data to download
url = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/'
PATH = '../data/isd/'
for i in range(count):
    usaf_id = data[i]['USAF']
    wban_id = data[i]['WBAN']
    year = datetime.strptime(data[i]['date'], '%Y-%m-%d').year
    #print(usaf_id, wban_id, year)
    filename = '{YEAR}/{USAF}-{WBAN}-{YEAR}.gz'.format(USAF=usaf_id, WBAN=wban_id, YEAR=year)
    url_filename = url+filename
    download_file = PATH+'{USAF}-{WBAN}-{YEAR}.gz'.format(USAF=usaf_id, WBAN=wban_id, YEAR=year)
    output_file = PATH+'{USAF}-{WBAN}-{YEAR}.txt'.format(USAF=usaf_id, WBAN=wban_id, YEAR=year)
    download(url_filename, download_file, output_file)


# ## d. Add pressure and temperature

# In[42]:


FILL_VAL = -9999
def checkTemperature(temperature1, temperature2):
    if temperature1.size==0:
        if temperature2.size==0:
            return FILL_VAL
        else:
            return temperature2.values[0]
    else:
        if temperature2.size==0:
            return temperature1.values[0]
        else:
            return (temperature1.values[0]+temperature2.values[0])/2

def checkPressure(pressure1, pressure2):
    if pressure1.size==0:
        if pressure2.size==0:
            return FILL_VAL
        else:
            return pressure2.values[0]
    else:
        if pressure2.size==0:
            return pressure1.values[0]
        else:
            return (pressure1.values[0]+pressure2.values[0])/2


# In[44]:


PATH = '../data/isd/'
for i in range(count):
    usaf_id = data[i]['USAF']
    wban_id = data[i]['WBAN']
    # need to check in case date1 is the last hour of the year; e.g: Dec 31, hour=23
    date1 = datetime.strptime('{date}-{time}'.format(date=data[i]['date'], time=data[i]['time_UTC']), '%Y-%m-%d-%H:%M:%S')
    date2 = date1 + timedelta(hours=1)
    filename = PATH+'{USAF}-{WBAN}-{YEAR}.txt'.format(USAF=usaf_id, WBAN=wban_id, YEAR=year)
    existing = os.path.isfile(filename)
    if not existing:
        print("File not found at: "+filename)
    else:
        columns = ['year','month','day','hour','air_temperature','dewpoint_temperature','sea_level_pressure','wind_direction','wind_speed_rate','sky_condition','precipitation_one_hour','precipitation_six_hour']
        df_isd = pd.read_fwf(filename, names=columns)
        # df_station[(df_station['BEGIN']<=plume_date)&(df_station['END']>=plume_date)]
        temperature1 = df_isd['air_temperature'][(df_isd['year']==date1.year)&(df_isd['month']==date1.month)&(df_isd['day']==date1.day)&(df_isd['hour']==date1.hour)]
        temperature2 = df_isd['air_temperature'][(df_isd['year']==date2.year)&(df_isd['month']==date2.month)&(df_isd['day']==date2.day)&(df_isd['hour']==date2.hour)]
        data[i]["air_temperature"] = checkTemperature(temperature1,temperature2)
        pressure1 = df_isd['sea_level_pressure'][(df_isd['year']==date1.year)&(df_isd['month']==date1.month)&(df_isd['day']==date1.day)&(df_isd['hour']==date1.hour)]
        pressure2 = df_isd['sea_level_pressure'][(df_isd['year']==date2.year)&(df_isd['month']==date2.month)&(df_isd['day']==date2.day)&(df_isd['hour']==date2.hour)]
        data[i]["sea_level_pressure"] = checkPressure(pressure1, pressure2)


# # Write data to JSON file

# In[46]:


def default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

outFile = '../data/merged/test_data.json'
with open(outFile, 'w') as fout:
    json.dump(data, fout, default=default)


# In[58]:


for i in range(count):
    print(data[i]['centroid_lat'],data[i]['centroid_lon'],data[i]['date'],data[i]['time_UTC'],data[i]['grace'],data[i]['ndvi'],data[i]['esi'],data[i]['air_temperature'],data[i]['sea_level_pressure'])
    


# In[55]:


df_new = pd.DataFrame(data)


# In[57]:


df_new.head()


# In[59]:


selected_columns =['centroid_lat','centroid_lon','date','time_UTC','grace','ndvi','esi','air_temperature','sea_level_pressure']
df_final = df_new[selected_columns]
df_final


# In[60]:


filename = '../data/merged/test_data_selected_cols.csv'
df_final.to_csv(filename, index=False)


# In[ ]:




