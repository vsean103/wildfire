#!/usr/bin/env python
# coding: utf-8

# In[1]:


from osgeo import osr, ogr
import gdal

PATH = "../data/esi_dataset/"
FILE_NAME = PATH + "DFPPM_4WK_2008162.tif"


# In[2]:


data = gdal.Open(FILE_NAME)
prj = data.GetProjection()
print(prj)
# srs=osr.SpatialReference(wkt=prj)
# if srs.IsProjected:
#     print(srs.GetAttrValue('projcs'))
# print(srs.GetAttrValue('geogcs'))


# In[3]:


# driver = gdal.GetDriverByName('tif')
transform = data.GetGeoTransform()

xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = -transform[5]   # negative coz from top to bottom 
print(xOrigin, yOrigin, pixelWidth, pixelHeight)
print(transform)


# In[4]:


lon, lat = -121, 39

# SpatialReference src = new SpatialReference();
src = osr.SpatialReference()
# src.SetWellKnownGeogCS("WGS84");
src.SetWellKnownGeogCS("WGS84")

# dataset = gdal.Open("path/to/my/file", gdalconstConstants.GA_ReadOnly);
dataset = gdal.Open(FILE_NAME)
# projection = dataset.GetProjection();
projection = dataset.GetProjection()
# SpatialReference dst = new SpatialReference(projection);
dst = osr.SpatialReference(projection)

# CoordinateTransformation ct = new CoordinateTransformation(src, dst);
ct = osr.CoordinateTransformation(src, dst)
# double[] xy = ct.TransformPoint(lon, lat);
xy = ct.TransformPoint(lon, lat)
# int x = (int)(((xy[0] - transform[0]) / transform[1]));
x = int(((xy[0] - xOrigin) / pixelWidth))
# int y = (int)(((xy[1] - transform[3]) / transform[5]));
y = int(((yOrigin - xy[1]) / pixelHeight))
x,y


# In[5]:


# band = data.GetRasterBand(1)
# arr = band.ReadAsArray()
data = dataset.ReadAsArray()
data[x,y]


# In[6]:


band = dataset.GetRasterBand(1)
arr = band.ReadAsArray()
print(arr.shape)
arr_min = arr.min()
arr_max = arr.max()
arr_mean = arr.mean()
print(arr_min, arr_max, arr_mean)
print(arr[x,y])


# In[ ]:




