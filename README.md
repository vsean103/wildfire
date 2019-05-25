# Wildfire

### Motivations:

Wildfire is considered one of the greatest destructive phenomena everywhere throughout the world. There have been more disastrous wildfires in recent years that caused irreversible environmental damage, including massive emissions of aerosols that can significantly affect air quality and regional-scale climate. What is more, wildfires can become a threat to property and more importantly human life. For example, last year (2018), there were a number of destructive wildfires in California.

In spite of the prominence of wildfires, current wildfire monitoring is still a challenge. Thus, this project aims to leverage publicly available datasets coupled with machine learning/deep learning techniques to help improve wildfire monitoring systems.

### Goals: 

* First, this project aims to make prediction whether or not it will initiate a wildfire, given an initial condition of surronding environment.

* Second, this project aims to make prediction on wildfire trajectory.

### Current stage: 

This repository contains python code for building data pipelines and parsers for required datasets that we need for this project.

## Getting Started


### Prerequisites

Some python packages/libraries: osgeo, gdal, glob, pyproj, h5py, pyhdf, numpy, pandas, os, gzip

## Data

The data that we have acquired so far is approximately 6 GBs so we cannot put them on here. The size is big because some datasets come in as image files like .tif or .hdf.

The final dataset representing wildfire condition is made up of important features from 5 different data sources
* MINX (plume data, location, date-time)
* GRACE (underground water)
* ESI (evaporative stress index)
* MODIS (NDVI index), and 
* ISD (air temperature and sea level pressure).

## Authors

* Viseth Sean
* Nick LaHaye

## Acknowledgments

* Collaborator: Nick LaHaye (JPL, Chapman University)
* Supervisors: Dr. Erik Linstead (Chapman University), Dr. Hesham El-Askary (Chapman University)
* ISD guidance from: William Brown, Meteorologist, NOAA's National Centers for Environmental Information, Center for Weather and Climate

## Challenges

We need to manually download MINX plume dataset because there is no available tool to get data for a particular region/state at a given period of time, at this time of our work (2019). We need location and datetime of plume data to download the other datasets accordingly.

To get more data:
* MINX: we need the plume filenames corresponding to any particular area (e.g. state or country) to download from the Plume website. (https://misr.jpl.nasa.gov/getData/accessData/MisrMinxPlumes2)
* GRACE: underground water data available from Jan 2008 to Jan 2015. (ftp://podaac-ftp.jpl.nasa.gov/allData/tellus/L3/gldas_monthly/ascii/)
* MODIS: from location and datetime of plume in MINX, need to find the right block of horizontal and vertical region to download; data available from 2000 to present. (https://e4ftl01.cr.usgs.gov/MOLT/MOD13Q1.006/)
* ESI: data available from 2001 to present. (https://gis1.servirglobal.net/data/esi/4WK/)
* ISD: data available since 1900s to present. (ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/)

Thus, it is best to get plume data that exists according to GRACE period (Jan 2008 to Jan 2015) because it’s the most limited dataset among the others.