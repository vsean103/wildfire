#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
import math
PATH = "../data/grace_dataset/csv/GLDAS_NOAH10_M.A200801.totalH2O.txt.csv"


# In[4]:


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


# In[5]:


df = pd.read_csv(PATH)


# In[9]:


df[:5]


# In[73]:


def reverse_convert_to_grace_longitude(x):
    # convert grace longitude 0-360 to -180 to 180
    return x-180

def convert_to_grace_longitude(x):
    return x+180


# In[78]:


long, lat = -118.821, 36.937
x1 = round(long) - 0.5
x2 = round(long) + 0.5
y1 = round(lat) - 0.5
y2 = round(lat) + 0.5
print(x1,y1)
print(x2,y2)


# In[79]:


x1 = convert_to_grace_longitude(x1)
x2 = convert_to_grace_longitude(x2)
long = convert_to_grace_longitude(long)
print(x1,y1)
print(x2,y2)
print(long, lat)


# In[80]:


type(df['LON'][1])


# In[81]:


def get_grace(df, lon, lat):
    qq = df[(df['LON']==x1) & (df['LAT']==y1)]['GRACE']
    return float(q11)


# In[82]:


q11 = get_grace(df, x1, y1)
q12 = get_grace(df, x1, y2)
q21 = get_grace(df, x2, y1)
q22 = get_grace(df, x2, y2)
q11, q12, q21, q22


# In[83]:


points = [(x1, y1, q11), (x1, y2, q12), (x2, y1, q21), (x2, y2, q22)]
bilinear_interpolation(long, lat, points)


# In[ ]:




