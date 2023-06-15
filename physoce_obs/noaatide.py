import os
from glob import glob
from calendar import monthrange
try:
    # For Python 3
    from urllib.request import urlretrieve
except ImportError:
    # Fall back to Python 2 urllib
    from urllib import urlretrieve
try:
    import pandas as pd
except ImportError:
	pass

def download_6min_csv(out_file, begin_date, end_date, station, product='water_level', datum='STND', time_zone='GMT'):
    """Download 6 minute water level or meteorology csv file from NOAA CO-OPS website.
    Uses API described at https://api.tidesandcurrents.noaa.gov/api/prod/

    Note that there is a limit of 31 days.

    Inputs:
        out_file - path and name of output file
        begin_date - 'YYYYMMDD' format (e.g. '20171201')
        end_date - 'YYYYMMDD' format (e.g. '20171231')
        station - string (e.g. '9413450' for Monterey)
        product - 'water_level','air_pressure', 'air_temperature' or 'wind'
                  (default 'water_level', which corresponds to 'hourly_height' on the NOAA API)
        datum - string (default 'STND' for station datum, see API link for more info/options)
                only used if product='water_level'
        time_zone - string (default 'GMT')
    """

    # Note: 6 minutes is the default interval, see https://api.tidesandcurrents.noaa.gov/api/prod/

    base_url = 'https://api.tidesandcurrents.noaa.gov'
    if product == 'water_level':
        api_url = '/api/prod/datagetter'\
        '?product='+product+\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&station='+station+\
        '&datum='+datum+\
        '&time_zone='+time_zone+\
        '&units=metric'\
        '&format=csv'
    else:
        api_url = '/api/prod/datagetter'\
        '?product='+product+\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&station='+station+\
        '&time_zone='+time_zone+\
        '&units=metric'\
        '&format=csv'

    url = base_url+api_url
    print(url)
    _retrieve_file(url,out_file)

def download_hourly_csv(out_file, begin_date, end_date, station, product='water_level', datum='STND', time_zone='GMT'):
    """Download hourly water level or meteorology csv file from NOAA CO-OPS website.
    Uses API described at https://api.tidesandcurrents.noaa.gov/api/prod/

    Note that there is a limit of 365 days.

    Inputs:
        out_file - path and name of output file
        begin_date - 'YYYYMMDD' format (e.g. '20171201')
        end_date - 'YYYYMMDD' format (e.g. '20171231')
        station - string (e.g. '9413450' for Monterey)
        product - 'water_level','air_pressure', 'air_temperature' or 'wind'
                  (default 'water_level', which corresponds to 'hourly_height' on the NOAA API)
        datum - string (default 'STND' for station datum, see API link for more info/options)
                only used if product='water_level'
        time_zone - string (default 'GMT')
    """

    base_url = 'https://api.tidesandcurrents.noaa.gov'
    if product == 'water_level':
        api_url = '/api/prod/datagetter'\
        '?product=hourly_height'\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&datum='+datum+\
        '&station='+station+\
        '&time_zone='+time_zone+\
        '&units=metric'\
        '&format=csv'
    else:
        api_url = '/api/prod/datagetter'\
        '?product='+product+\
        '&application=NOS.COOPS.TAC.WL'\
        '&begin_date='+begin_date+\
        '&end_date='+end_date+\
        '&station='+station+\
        '&time_zone='+time_zone+\
        '&units=metric'\
        '&interval=h'\
        '&format=csv'

    url = base_url+api_url
    _retrieve_file(url,out_file)

def _retrieve_file(url,out_file):
    '''Helper function to retrieve data through NOAA CO-OPS API

    Used by download_hourly_csv() function. For further information on NOAA CO-OPS API calls, visit https://api.tidesandcurrents.noaa.gov/api/prod/

    Inputs:
        url - URL which makes a web service call through the API
        out_file - path and name of output file
    '''

    urlretrieve(url,out_file)

    # check whether data file is valid
    f = open(out_file, 'r')
    line1 = f.readline()
    line2 = f.readline()
    if (not line1.startswith('Date Time,')) or (line2.startswith('Error')):
        print('Warning: not a valid file: '+out_file)
        print(f.read()) # print error message in file
        os.remove(out_file)
    f.close()

def download_multiyear_csv(out_dir, years, station, product='water_level', datum='STND', time_zone='GMT'):
    """Download multiple one-year hourly csv files from NOAA CO-OPS website (one file per year).
    Uses API described at https://api.tidesandcurrents.noaa.gov/api/prod/

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
        out_file = os.path.join(out_dir,file_prefix+str(year)+'.csv')
        begin_date = str(year)+'0101'
        end_date = str(year)+'1231'
        download_hourly_csv(out_file,begin_date,end_date,station,product,datum,time_zone)

def download_multimonth_csv(out_dir, year_start, month_start, year_end, month_end, station, product='water_level', datum='STND', time_zone='GMT'):
    """Download multiple one-month csv files of 6-minute interval data from NOAA CO-OPS website (one file per month).
    Uses API described at https://api.tidesandcurrents.noaa.gov/api/prod/

    * Creates output directory if it does not exist, but its parent directory does exist.
    * Files are saved as [station]_[product]_[year]_[month].csv (e.g. 9413450_water_level_2020_06.csv)

    Inputs:
        out_dir - path and name of output directory
        year_start - year to start download (e.g. 2020)
        month_start - month to start download (e.g. 6, for June)
        year_end - year to end download
        month_end - month to end download
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

    years = range(int(year_start),int(year_end)+1)

    for year in years:
        if year == years[0]:
            mon_range = range(month_start,13)
        elif year == years[-1]:
            mon_range = range(1,month_end+1)
        else:
            mon_range = range(1,13)

        for mon in mon_range:
            mon_str = str(mon).zfill(2)

            # file to write
            filename = file_prefix+str(year)+mon_str+'.csv'
            out_file = os.path.join(out_dir,filename)

            # determine number of days in month
            ndays = monthrange(year, mon)[1]
            ndays_str = str(ndays).zfill(2)

            begin_date = str(year)+mon_str+'01'
            end_date = str(year)+mon_str+ndays_str

            download_6min_csv(out_file, begin_date, end_date, station, product, datum, time_zone)

def csv_to_dataframe(data_dir,pattern='*.csv'):
    ''' Create pandas dataframe from directory of NOAA tide gauge csv files. Useful
    for combining and loading csv files created by noaatide.download_multiyear_csv()
    because individual files are limited to 365 days for hourly data.

    Inputs:
        data_dir - path to directory where csv files are located
        pattern - pattern indicating which files to use (default '*.csv')
    '''
    file_list = sorted(glob(os.path.join(data_dir,pattern)))
    df = pd.DataFrame()
    dflist = []
    for file in file_list:
        dflist.append(pd.read_csv(file,usecols=[0,1],index_col=0,parse_dates=True,skipinitialspace=True))
    df = pd.concat(dflist)
    return df

if __name__ == '__main__':
    # Test download of 6-min csv files
    import shutil
    os.mkdir('tmp_csv_download')
    download_multimonth_csv('tmp_csv_download', 2017, 11, 2018, 1, '9413450')
    os.listdir('tmp_csv_download')
    shutil.rmtree('tmp_csv_download')
