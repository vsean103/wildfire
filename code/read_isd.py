#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[3]:


PATH = "../data/isd/724917-23233-2008.txt"


# In[4]:


colspecs=[[1,4], [6,7], [9,11], [12,13], [14,19], [20,24], [26,31], [32,37], [38,43], [44,49], [50,55], [56, 61]]
# df = pd.read_fwf(PATH, colspecs=colspecs, header=0)
columns = ['year','month','day','hour','air_temperature','dewpoint_temperature','sea_level_pressure','wind_direction','wind_speed_rate','sky_condition','precipitation_one_hour','precipitation_six_hour']
df = pd.read_fwf(PATH, names=columns)  # colspecs = 'infer'


# In[6]:


df


# In[ ]:




