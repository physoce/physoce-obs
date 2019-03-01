import numpy as np
import pandas as pd
import xarray as xr
from calendar import isleap

def get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out=None,start_day=None,end_day=None,spatialresolution = '4km',
                          varname='chl_ocx',varcategory='CHL',timeresolution='DAY',mapping='L3m',file_prefix='A',
                          opendap_dir = 'https://oceandata.sci.gsfc.nasa.gov:443/opendap/MODISA/L3SMI/'):
    '''
Extract a subset of data using the NASA Ocean Color OpenDAP server at https://oceandata.sci.gsfc.nasa.gov/opendap

The OpenDAP server provides individual NetCDF files Returns a regional dataset with a time axis.

year_range - a list of two numbers specifying start and end years for the download
lat_extent - a list of two numbers specifying a range of latitudes to extract
lon_extent - a list of two numbers specifying a range of longitudes to extract
netcdf_out - path to a NetCDF file containing the output (optional)
start_day - year day to start downloading data in first year (optional)
end_day - year day to finish downloading data in first year (optional)

Additional parameters are used to specify the file name, e.g.
https://oceandata.sci.gsfc.nasa.gov:443/opendap/MODISA/L3SMI/2004/001/A2004001.L3m_DAY_CHL_chl_ocx_4km.nc
Deafult values are for MODIS Aqua chlorophyll-a (OCX algorithm)

varcategory - uppercase string specifiying category of variable, e.g. 'CHL', 'FLH' or 'RRS' (default 'CHL')
varname - lowercase string specifiying variable name within the category, e.g. 'chl_ocx', 'nflh' or 'Rrs_555' (default 'chl_ocx')
timeresolution - 'DAY','8D','MO','R32' or 'YR' (default 'DAY')
spatialresolution = '4km' or '9km' (default '4km')
mapping - default 'L3M'
file_prefix - string for first part of filename before date information (default 'A')
opendap_dir - directory containing files on server (default 'https://oceandata.sci.gsfc.nasa.gov:443/opendap/MODISA/L3SMI/'')
    '''
    
    file_id = (mapping+'_'+timeresolution+'_'+varcategory+'_'+
               varname+'_'+spatialresolution)
    
    if type(year_range) is int:
        all_years = [year_range]
    elif len(year_range) == 1:
        all_years = year_range
    elif len(year_range) == 2:
        all_years = np.arange(year_range[0],year_range[1]+1)

    # number of days in each year to be downloaded
    ndays = np.nan*np.zeros(len(all_years))
    for yi,year in enumerate(all_years):
        if isleap(year):
            nd = 366
            ndays[yi] = 366
        else:
            nd = 365
            ndays[yi] = 365
        if (yi == 0) and start_day:
            ndays[yi] = ndays[yi]-start_day+1
        if (yi == len(all_years)-1) and end_day:
            ndays[yi] = ndays[yi]-(nd-end_day)

    print('all_years',all_years)
    print('ndays',ndays)
    
    
    ntotal = int(sum(ndays))

    lat_extent = np.array(lat_extent)
    lon_extent = np.array(lon_extent)

    ti = 0
    for yi,year in enumerate(all_years):
        
        # start and end days (default entire year)
        dstart = 1
        if isleap(year):
            dend = 366
        else:
            dend = 365
        
        # if start or end days are specified
        if (yi == 0) and (start_day is not None):
            dstart = start_day
        if (yi == len(all_years)-1) and (end_day is not None):
            dend = end_day
            
        print('dstart',dstart)
        print('dend',dend)
        print('start_day',start_day)
        print('end_day',end_day)
        
        for day in np.arange(dstart,dend+1):
            print(str(year)+', '+str(int(day)))
            date_idstr = (str(year)+'/'+str(int(day)).zfill(3)+
                          '/'+file_prefix+str(year)+str(int(day)).zfill(3))

            file_url = opendap_dir+date_idstr+'.'+file_id+'.nc'

            for i in range(10): # try 10 times
                try:
                    ds = xr.open_dataset(file_url)
                    if ti==0:
                        ii, = np.where((ds.lat >= lat_extent[0]) & 
                                       (ds.lat <= lat_extent[1]))
                        jj, = np.where((ds.lon >= lon_extent[0]) & 
                                       (ds.lon <= lon_extent[1]))
                        time = np.empty(ntotal, dtype='datetime64[D]')
                        dsout = xr.Dataset(
                            {varname: (('time','lat','lon'), np.nan*np.zeros([ntotal,len(ii)-1,len(jj)-1]))},
                            {'time': time,
                             'lat': np.array(ds.lat[ii[:-1]]),
                             'lon': np.array(ds.lon[jj[:-1]])})
                        dsout[varname].attrs = ds[varname].attrs
                        dsout['lon'].attrs = ds['lon'].attrs
                        dsout['lat'].attrs = ds['lat'].attrs
                        dsout.attrs['notes'] = ('Created by nasa.get_oceancolor_dataset,' +
                                                str(np.datetime64('now')))

                    dsub = ds.isel(lat=slice(ii[0],ii[-1]),
                                   lon=slice(jj[0],jj[-1]))
                    ds.close()

                    t = pd.to_datetime(str(year)+'-'+str(int(day)).zfill(3),format='%Y-%j').to_datetime64()
                    time[ti] = t
                    dsout[varname][ti,:,:] = dsub[varname]

                    break
                except:
                    print(str(i+1)+'/10 could not open: '+file_url)
            ti=ti+1

    print('download finished')

    dsout['time'] = time
    
    if netcdf_out is not None:
        dsout.to_netcdf(netcdf_out)
        
    return dsout
    
if __name__ == '__main__':
    ### Test the get_oceancolor_dataset function for different time parameters
    
    netcdf_out = None
    lat_extent = [34.5,38.5]
    lon_extent = [-124.5,-120.5]
    
    year_range = [2004]
    start_day = 2
    end_day = 5
    ds1 = get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out,start_day,end_day)
    
    year_range = 2004
    ds2 = get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out,start_day=364)
    
    year_range = 2003
    ds3 = get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out,start_day=364)
    
    year_range = 2003
    ds4 = get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out,end_day=3)
    
    year_range = [2004,2005]
    ds5 = get_oceancolor_dataset(year_range,lat_extent,lon_extent,netcdf_out,start_day=364,end_day=2)