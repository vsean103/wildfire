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

* Collaborator: Nick LaHaye
* Supervisors: Dr. Erik Linstead, Dr. Hesham El-Askary

