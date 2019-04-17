import json
import pandas as pd
import math
from pprint import pprint
from pyhdf import SD
import numpy as np
import matplotlib.pyplot as plt
import sys
import h5py
import time
import calendar
from datetime import datetime
import glob
from pyproj import Proj


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

def reverse_convert_to_grace_longitude(x):
    # convert grace longitude 0-360 to -180 to 180
    return x-180

def convert_to_grace_longitude(x):
    return x+180

def get_grace(df, lon, lat):
    qq = df[(df['LON']==lon) & (df['LAT']==lat)]['GRACE']
    return float(qq)


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


PATH_MODIS = "../data/modis_dataset/"
# FILE_NAME = PATH + "MOD13Q1.A2008161.h08v05.006.2015176070634.hdf"
# start_day_of_year = 161
# year = 2008 # data[i]['date']
p_modis_grid = Proj('+proj=sinu +R=6371007.181 +nadgrids=@null +wktext')
def get_modis_ndvi(day_of_year, year):
    filename = PATH_MODIS + "*.A"+str(year)+"*"+str(day_of_year)+"*.hdf"
    name = glob.glob(filename)[0]
    # print(name)
    hdf=SD.SD(name)
    # Get the selected dataset
    ndvi = hdf.select('250m 16 days NDVI')
    # get the data
    ndvi = ndvi[:]
    lon, lat = data[i]['centroid_lon'], data[i]['centroid_lat']
    im_x, im_y = convert_global_xy_to_grid_xy(lon, lat)
    x, y = round(im_x), round(im_y)
    return ndvi[x,y]


#### Load MINX data
PATH_MINX = "../data/plume_dataset/plume_test.json"

with open(PATH_MINX) as f:
    data = json.load(f)

pprint(data)

count = len(data)



##### Add centroid of fire, based on polygon tables from MINX
for i in range(count):
    xs = data[i]['polygon']['lon']
    ys = data[i]['polygon']['lat']
    x, y = (sum(xs) / len(xs)), (sum(ys) / len(ys))
    data[i]['centroid_lon'] = round(x,2)
    data[i]['centroid_lat'] = round(y,2)

print('**** Add centroid of fire, based on polygon tables from MINX ****')
print('Lon, Lat')
for i in range(count):
    print(str(data[i]['centroid_lon']) + ', ' + str(data[i]['centroid_lat']))



##### Add underground water from GRACE
print('**** Add underground water from GRACE ****')
PATH_GRACE = "../data/grace_dataset/csv/"

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

    df = pd.read_csv(PATH_GRACE+filename)
    q11 = get_grace(df, x1, y1)
    q12 = get_grace(df, x1, y2)
    q21 = get_grace(df, x2, y1)
    q22 = get_grace(df, x2, y2)
    points = [(x1, y1, q11), (x1, y2, q12), (x2, y1, q21), (x2, y2, q22)]
    grace = bilinear_interpolation(lon, lat, points)
    data[i]['grace'] = round(grace,2)
    print(data[i]['grace'])


#### Add NDVI from MODIS
print('**** Add NDVI from MODIS ****')
for i in range(count):
    day_of_year = datetime.strptime(data[i]['date'], '%Y-%m-%d').timetuple().tm_yday
    year = datetime.strptime(data[i]['date'], '%Y-%m-%d').year
    start = 16 * math.floor(int(day_of_year)/16) + 1
    end = start + 16
    start_ndvi = get_modis_ndvi(start, year)
    end_ndvi = get_modis_ndvi(end, year)
    data[i]['ndvi'] = round((start_ndvi+end_ndvi)/2, 2)
    print(data[i]['ndvi'])


#### Add ESI from ESI Tif files
import gdal
ds = gdal.Open(filename)
data = ds.ReadAsArray()
