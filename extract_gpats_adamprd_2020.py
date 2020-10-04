import cx_Oracle
import io
import requests
from pandas.io import sql
import pandas as pd
import matplotlib.pyplot as plt
#%matplotlib inline

def get_sta_latlon(sta):
    sta = sta.upper()
    lat_lon = avlocs[avlocs['type'] == 'AD'].loc[sta][['latitude','longitude']].values
    return lat_lon

from io import StringIO

avlocs_url = 'http://web.bom.gov.au/cosb/dms/mgdu/avloc/avloc.csv'
s=requests.get(avlocs_url).text
avlocs = pd.read_csv(StringIO(s), header=0, sep=';', comment='#', index_col='av_id')

#s=requests.get(avlocs_url).content
#avlocs = pd.read_csv(io.StringIO(s.decode('utf-8')), header=0, sep=';', comment='#', index_col='av_id')

#import ast
#raw_value = input("Enter station or airport name: ")
#sta_name = ast.literal_eval(raw_value)


'''
sta_name = input("Enter station or airport name: ")
#sta_name = 'Holsworthy' 
print ('\nRecords matching airport name')
print(avlocs[avlocs['name'].str.contains(sta_name.upper(), case=False)])

# .str.contains() is case sensitive. Disregard case - .str.contains(case=False).
# print(avlocs[avlocs['name'].str.endswith(sta_name.upper())])
# Lots of locations with same name. airport -> 'type'] == 'AD'

print('\nAviation Ids matching aviation name')
match_idx = avlocs[ avlocs['name'].str.contains(sta_name.upper(), case=False)].index.tolist()
print (match_idx)

'''
'''
Above should print a list of matching sta_ids i.e the index of all matching rows
Now we need to use that list to pull out rows macthing indexes and find one that 
has type=='AD'
'''

'''
print('\nAviation Id for actual aerodrome - to get lat and long coords')
tmp = avlocs.loc[match_idx]
id =  tmp[ tmp['type'] == 'AD'].index.tolist()

print(avlocs[ avlocs['type'] == 'AD'].loc[id[0].upper()])
  
print (get_sta_latlon(id[0]))

(location_lat,location_lon) = get_sta_latlon(id[0])
print (location_lat,location_lon)

print ("Sample file name: /tmp/"+id[0].upper()+"_gpats.csv")
'''


'''
Sample run to demostrate that correct lat long coordinates is being used.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
(default_py2) [vinorda@qld-vw-dev gpats]$ python ./extract_gpats_adamprd_new.py
Enter station or airport name: sunshine

Records matching airport name
                                   name  latitude  longitude type region state
av_id                                                                         
BSUNA  SUNSHINE COAST RWY18 RIGHT INI A -26.37276  153.12664  GNA     YB   QLD
BSUNC  SUNSHINE COAST RWY18 CEN INIT AP -26.36260  153.23252  GNA     YB   QLD
BSUND  SUNSHINE COAST RWY18 LEFT INIT A -26.44873  153.27940  GNA     YB   QLD
BSUNF    SUNSHINE COAST RWY18 FINAL APP -26.50898  153.14270  GNA     YB   QLD
BSUNH  SUNSHINE COAST RWY18 MIS AP HOLD -26.67970  153.18698  GNA     YB   QLD
BSUNI    SUNSHINE COAST RWY18 INTER APP -26.43580  153.18764  GNA     YB   QLD
BSUNM   SUNSHINE COAST RWY18 MISSED APP -26.58211  153.09773  GNA     YB   QLD
SHY                            SUNSHINE  38.04062  -92.60241  VOR     K3   NaN
SHY                            SUNSHINE  38.04062  -92.60241  DME     K3   NaN
SU                       SUNSHINE COAST -26.59219  153.09171  NDB     YB   QLD
SU                       SUNSHINE COAST -26.59768  153.09030  VOR     YB   QLD
SU                       SUNSHINE COAST -26.59768  153.09030  DME     YB   QLD
SU012         SUNSHINE COAST RWY18 FROP -26.56193  153.10333  GNA     YB   QLD
SU035    SUNSHINE COAST RWY18 FINAL APP -26.52301  153.15896  GNA     YB   QLD
SU073    SUNSHINE COAST RWY18  TURN CEN -26.57453  153.15889  GNA     YB   QLD
SU134  SUNSHINE COAST RWY18 TURN CENTRE -26.64438  153.14954  GNA     YB   QLD
SU139   SUNSHINE COAST RWY18 MISSED APP -26.70468  153.21132  GNA     YB   QLD
SU157     SUNSHINE COAST RWY18 TURN END -26.70463  153.14946  GNA     YB   QLD
SU192   SUNSHINE COAST RWY18 MISSED APP -26.62966  153.08452  GNA     YB   QLD
YBSU                     SUNSHINE COAST -26.60342  153.09104   AD     YB   QLD
YBSU                     SUNSHINE COAST -26.60556  153.08750  ABN     YB   QLD
YXHS            SUNSHINE COAST HOSPITAL -26.74732  153.11368  HLS     YB   QLD

Aviation Ids matching aviation name
['BSUNA', 'BSUNC', 'BSUND', 'BSUNF', 'BSUNH', 'BSUNI', 'BSUNM', 'SHY', 'SHY', 'SU', 'SU', 'SU', 'SU012', 'SU035', 'SU073', 'SU134', 'SU139', 'SU157', 'SU192', 'YBSU', 'YBSU', 'YXHS']

Aviation Id for actual aerodrome - to get lat and long coords
name         SUNSHINE COAST
latitude           -26.6034
longitude           153.091
type                     AD
region                   YB
state                   QLD
Name: YBSU, dtype: object
[-26.60342 153.09103999999999]
(-26.60342, 153.09103999999999)
Sample file name: /tmp/YBSU_gpats.csv

'''



# maxlon = location.lon + get_lon_10nm(location.lat);
# minlon = location.lon - get_lon_10nm(location.lat);
start_date = '2000-01-01'
end_date   = '2020-09-29'

# LAT_5NM =  0.08333; # degrees; 1 degree of latitude = 60 nautical miles
LAT_10NM = 0.16666; # degrees; 1 degree of latitude = 60 nautical miles
#LAT_30NM = 0.5; # degrees; 1 degree of latitude = 60 nautical miles

# id1 = ['YBSU','YBCG', 'YAMB','YBAF','YTWB','YBOK']
# id='YBBN','YBSU','YBCG','YAMB','YBAF','YTWB','YSSY','YWOL','YWLM','YSRI',
id1=['YSBK','YSCN','YSHW','YPDN','YBAS','YMML','YPPH','YPAD','YSCB']
id1=['YBOK','YBWW','YBRK','YBRM','YPPD','YPTN','YPCC','YPXM']
#for sta_id in defence:
for sta_id in id1:
    
    print("\n#######################################\nBegin Processing "+sta_id.upper())
          
    (location_lat,location_lon) = get_sta_latlon(sta_id)
    print (get_sta_latlon(sta_id))
    
    (location_lat,location_lon) = get_sta_latlon(sta_id)
    print (location_lat,location_lon)  
    
    minlat = location_lat - LAT_10NM;
    maxlat = location_lat + LAT_10NM;
    minlon = location_lon - LAT_10NM;
    maxlon = location_lon + LAT_10NM; # use approximate longitude range!


    my_query = ( "SELECT TM,LATITUDE,LONGITUDE,AMP FROM GPATS_LTNG "
        "WHERE TM >= TO_DATE('{start}', 'yyyy-mm-dd:hh24')"
          "AND TM <= TO_DATE('{end}'  , 'yyyy-mm-dd:hh24')"
            "AND LATITUDE <= {maxlat}"
            "AND LATITUDE >= {minlat}"
            "AND LONGITUDE <= {maxlon}"
            "AND LONGITUDE >= {minlon}"
            "AND AMP != 0"
        "ORDER BY TM"
    ).format(
    start=start_date, end=end_date,\
    minlat=minlat, maxlat=maxlat, \
    minlon=minlon, maxlon=maxlon
    )

    conn = cx_Oracle.connect(user='anonymous', password='anonymous', dsn = 'adamprd')
    cursor = conn.cursor()

    print("Reading gpats data for "+sta_id.upper()+" from ADAM...")
    df = sql.read_sql(my_query, conn, parse_dates = True, index_col='TM')
    
    print("Writing data to \tmp local filesystem...")
    print ("/tmp/data/"+sta_id.upper()+"_gpats2020_10NM.csv")
    df.to_csv("/tmp/data/"+sta_id.upper()+"_gpats2020_10NM.csv", sep=',', header=True, index=True)

