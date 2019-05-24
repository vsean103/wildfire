#!/usr/bin/env python
# coding: utf-8

# In[16]:


import csv
import re


# In[17]:


PATH = "../data/grace_dataset/"
# NAME = "GLDAS_NOAH10_M.A200801.totalH2O"
# FILE_NAME = PATH + NAME + ".txt"
# OUT_FILE = PATH + 'csv/' NAME + '.csv'


# In[25]:


def read_grace_to_csv(filename):
    name = filename.split("/")[-1]
    out_file = PATH + 'csv/' + name + '.csv'
    with open(filename, 'r') as in_file:
        # skip first 19 lines
        for _ in range(19):
            next(in_file)
        # strip spaces in front and the back
        stripped = (line.strip() for line in in_file)
        # strip spaces in between
        stripped = (re.sub(' +', ' ', line) for line in stripped)
        lines = (line.split(" ") for line in stripped if line)
        with open(out_file, 'w') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(('LON', 'LAT', 'GRACE'))
            writer.writerows(lines)        


# In[26]:


import glob
import errno


# In[27]:


file_path = '../data/grace_dataset/*.txt'
files = glob.glob(file_path)
for name in files:
    try:
        read_grace_to_csv(name)
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise


# In[ ]:




