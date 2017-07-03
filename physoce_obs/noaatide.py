#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    # For Python 3
    from urllib.request import urlretrieve
except ImportError:
    # Fall back to Python 2 urllib
    from urllib import urlretrieve

def download_hourly_csv(out_file,begin_date,end_date,station,product='water_level',datum='STND'):
    """Download hourly water level csv file from NOAA CO-OPS website.
    Uses API described at https://tidesandcurrents.noaa.gov/api
    
    Note that there is a limit of 365 days.
    
    Inputs:
        out_file - path and name of output file
        begin_date - 'YYYYMMDD' format (e.g. '20171201')
        end_date - 'YYYYMMDD' format (e.g. '20171231')
        station - string (e.g. '9413450' for Monterey)
        product - 'water_level','air_pressure', 'air_temperature' or 'wind'
                  (default 'water_level')
        datum - string (default 'STND' for station datum, see API link for more info/options)
                only used if product='water_level'
    """
    
    base_url = 'https://tidesandcurrents.noaa.gov'
    if product is 'water_level':
        api_url = '/api/datagetter'\
        '?product=hourly_height'\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&datum='+datum+\
        '&station='+station+\
        '&time_zone=GMT'\
        '&units=metric'\
        '&format=csv'
    else:
        api_url = '/api/datagetter'\
        '?product='+product+\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&station='+station+\
        '&time_zone=GMT'\
        '&units=metric'\
        '&interval=h'\
        '&format=csv'

    url = base_url+api_url
    urlretrieve(url,out_file)
    
    # check whether data file is valid
    f = open(out_file, 'r')
    line = f.readline()
    if not line.startswith('Date Time,'):
        print('Warning: not a valid file: '+out_file)
        print(f.read()) # print error message in file
        os.remove(out_file) 
    f.close()
    
def download_multiyear_csv(out_dir,years,station,product='water_level',datum='STND'):
    """Download multiple one-year csv files from NOAA CO-OPS website (one file per year).
    
    * Creates output directory if it does not exist, but its parent directory does exist.
    * Files are saved as [station]_[product]_[year].csv (e.g. 9413450_air_pressure_2015.csv)
    
    Inputs:
        out_dir - path and name of output directory
        years - list of years to download 
        station - string (e.g. '9413450' for Monterey)
        product - 'water_level','air_pressure', 'air_temperature' or 'wind'
                  (default 'water_level')
        datum - string (default 'STND' for station datum, see API link for more info/options)
                only used if product='water_level'
    """
                  
    # add trailing slash to directory name, if necessary
    if out_dir[-1] is not ('/' or '\\'):
        out_dir = out_dir+'/'
    
    # create directory if necessary
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    
    file_prefix = station+'_'+product+'_'
    for year in years:
        out_file = out_dir+file_prefix+str(year)+'.csv'
        begin_date = str(year)+'0101'
        end_date = str(year)+'1231'
        download_hourly_csv(out_file,begin_date,end_date,station,product,datum)