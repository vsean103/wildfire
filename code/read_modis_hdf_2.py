#!/usr/bin/env python
# coding: utf-8

# In[2]:


#import necessary modules
from pyhdf import SD
import numpy as np
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
import sys
import h5py
import time
import calendar


# In[6]:


PATH = "../data/modis_dataset/"
FILE_NAME = PATH + "MOD13Q1.A2008161.h08v05.006.2015176070634.hdf"

hdf=SD.SD(FILE_NAME)


# In[7]:


hdf.datasets()


# In[8]:


# Get the selected dataset
ndvi = hdf.select('250m 16 days NDVI')


# In[9]:


# Not the attributes that you're looking for
ndvi.attributes()


# In[10]:


ndvi.dimensions()


# In[11]:


# get the data
ndvi = ndvi[:]
min_ndvi=ndvi.min()
max_ndvi=ndvi.max()


# In[12]:


print('Min NDVI: ', min_ndvi)
print('Max NDVI: ', max_ndvi)


# In[13]:


print(ndvi)


# In[19]:


ndvi.shape


# In[21]:


from pyproj import Proj

p_modis_grid = Proj('+proj=sinu +R=6371007.181 +nadgrids=@null +wktext')
# from lon, lat to x, y
# x, y = p_modis_grid(lon, lat)
# # or the inverse, from x, y to lon, lat
# lon, lat = p_modis_grid(x, y, inverse=True)


# In[22]:


lon, lat = -122.669, 39.876
x, y = p_modis_grid(lon, lat)
x, y


# In[23]:


lon, lat = -118.821, 36.937
x, y = p_modis_grid(lon, lat)
x,y


# In[25]:


#You have global map coordinates there which need to be #translated into x/y relative to the specific grid:

upper_ul_x = -20015109.354
upper_ul_y = 10007554.677
tile_h = 8
tile_v = 5
pixel_resolution_m = 500
tile_resolution_m = 1200000

x,y = p_modis_grid(-122,39)

im_ul_x = upper_ul_x + tile_h*tile_resolution_m
im_ul_y = upper_ul_y - tile_v*tile_resolution_m


im_x = (im_ul_x - x)/pixel_resolution_m
im_y = (y - im_ul_y)/pixel_resolution_m

im_x, im_y


# In[29]:


round(im_x), round(im_y)


# In[30]:


x, y = round(im_x), round(im_y)
ndvi[x,y]


# In[ ]:




