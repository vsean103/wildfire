#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


PATH = "../data/isd/isd-history_w_header.txt"

# df = pd.read_csv(PATH, delim_whitespace=True, header=None)
# df = pd.read_csv(PATH, delimiter=r"\s+")
# data.columns = ['USAF','WBAN','STATION','NAME','CTRY','ST','CALL','LAT','LON','ELEV(M)','BEGIN','END']


# In[3]:


colspecs=[[0,7], [7,13], [13,43], [43,48], [48,51], [51,57], [57,65], [65,74], [74,82], [82,91], [91,100]]
df = pd.read_fwf(PATH, colspecs=colspecs, header=0)


# In[4]:


df.head()


# In[5]:


df.tail()


# In[6]:


df_cali = df[(df['CTRY']=='US')&(df['ST']=='CA')]
len(df_cali)


# In[9]:


df.to_csv('../data/isd/isd_station.csv', index=False)


# In[10]:


df_cali.isnull().values.any()


# In[11]:


df_cali.isnull().T.any().T.sum()


# In[12]:


nan_rows = df_cali[df_cali.isnull().T.any().T]


# In[13]:


nan_rows


# In[14]:


# remove station without either LAT or LON
df_cali = df_cali[pd.notnull(df_cali['LAT'])]
df_cali = df_cali[pd.notnull(df_cali['LON'])]
len(df_cali)


# In[15]:


df_cali.to_csv('../data/isd/isd_station_cali.csv', index=False)


# In[ ]:




