import numpy as np
import pandas as pd
import requests
import seaborn as sb
#from collections import namedtuple
from datetime import datetime, timedelta #,date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

import pickle
import cx_Oracle
from pandas.io import sql

import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as etree
import sys
import os
#import wget
import re

import logging
logger = logging.getLogger('stormers')

from flask import redirect,session
# cur_dir = os.path.dirname(__file__)

'''need this variable declaration here for scripts that refer
   to data files stored here '''

# cur_dir = '/home/accounts/vinorda/sr-ask-11966/data/'
# cur_dir = '/home/accounts/vinorda/data/'
# cur_dir = '/home/bou/windows-shared/data/'


# taf lists for individidual ARFOR areas.
area40 = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YTWB','YBOK','YBWW',\
          'YHBA','YMYB','YBUD','YGLA','YBRK','YKRY','YTNG','YSMH' ]
area41 = ['YROM', 'YSGE','YBCV', 'YLRE','YBDV', 'YLLE', 'YWDH','YTGM']
area43 = ['YBMA', 'YCCY', 'YJLC', 'YRMD', 'YHUG', 'YTMO', 'YTEE', 'YWTN']
area44 = ['YBTL', 'YBMK', 'MKY', 'YBPN','YBHM', 'YEML', 'YMRB', 'YCMT' ]
area45 = ['YBCS','YBWP','YHID','YLHR','YCKN','YGTN','YIFL',\
          'YMBA','YCOE','YNTN','YBKT','YCNY','YMTI','YKOW','YBSG','YLZI']

qld = area40+area41+area43+area44+area45
nt = ['YBAS','YAYE', 'YBTI', 'YSNB','YJVN','YBYU', 'YPDN', 'WPDL', 'YELD', 'YPGV', 'YGTE', 'YHOO',\
    'YJAB', 'YMGD', 'YMGB','YMHU','YNGU','YPKT','YPTN','YTNK','YTGT','YYND','YGLS','YKNT']
wa = ['YARG','YBRY','YBWX','YBGD','YBRM','YCHK','YPXM','YPCC','YCWA','YDBY','YFTZ','YTST'\
    'YFDF','YHLC','YPKA','YPKU','YWYM','YLBD','YTTI','YNWN','YOLW','YPBO','YPPD','YCIN',\
    'YPLM','YSOL','YTEF','YANG',\
    'YBLW','YGEL','YPJT','YMOG','YPEA','YPPH','YRTI','YFRT','YABA','YBUN','YBLN','YESP','YCAR','YSHK']
nsw=['YARM','YBNA','YSBK','YBTH','YSCN','YCNK','YCFS','YCBB','YSDU','YGLI','YGFN','YKMP','YLIS',\
    'YLHI','YMND','YMOR','YMDG','YNBR','YSNF','YSNW','YORG','YPKS','YPMQ','YSRI','YSCO','YSSY','YSTW',\
    'YTRE','YWLM','YSCB','YCOM','YGLB','YSHW','YSHL','YMER','YMRY','YSWG','YYNG']
vic=['YMAY','YMAV','YBNS','YBLT','YBDG','YMES','YMEN','YFLI','YHML','YHSM','YKII','YLTV','YMNG','YMML',\
    'YMIA','YMMB','YMTG','YPOD','YREN','YSHT','YSWH','YWGT','YWBL']
sa=['YPAD','YPED','YKSC','YMTG','YPPF','YPAG','YPLC','YWHA','YBHI','YCBP','YLEC','YMIA','YOLD','YPWR',\
    'YOOM','YCDU','YFRT','YWUD']

defence = ['YPCC', 'YPXM', 'YPDN', 'YPTN', 'YCIN', 'YPLM', 'YBSG', 'YBTL', 'YBOK', 'YAMB',\
           'YWLM', 'YSRI', 'YSCB', 'YSNW', 'YMES', 'YMPC', 'YPED', 'YPWR', 'YPEA','YSHW',\
           'YSBK','YARM','YCNK','YSCO','YSTW','YCOM','YSWG']

#https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
#import json
#preci_metadata_file = 'precis_metadata.json'
#taf_metadata_file = 'taf_metadata.json'
#with open(filename, 'r') as f:
#    datastore = json.load(f)
#    for sta in nt:
#        print(sta, ' Name: ' + datastore[sta]['NAME'])
#    for sta in nt+wa:
#        print(sta, ':', datastore[sta]['WMO_NUM'] )
#        print(sta, ':', datastore[sta]['BOM_ID'] )


'''pdl 97390  'YYND':94324 - only 9am synops-> use Territory Grape Farm TGFM 94328,'YTGT':use Rabbit Flats 95322
Bathurst Is YBTI uses Point Fawcett 94122 which is actually on the far west coast of the island and gets NW to SW seabreeze
YBTI is almost near Wurrumiyanga (the preci location) - this is on the far east coast so gets SE seabreeze no vi/ceilo here!
YBYU':99126
BAYU UNDAN (LIBERDADE SHIP)  401476
http://sdbweb.bom.gov.au:8891/sitesdb/plsql/SDB_SD_details.p?NstnNum=401476&stnsysID=
'''

#avid to wmo number mappings
avid_wmo_dict = \
    {'YBBN':94578,'YBAF':94575,'YAMB':94568,'YBSU':94569,'YBCG':94592,\
    'YTWB':95551,'YBOK':94552,'YBWW':99435,'YHBA':95565,'YMYB':94567,'YBUD':94387,\
     'YGLA':94381,'YBRK':94374,'YSMH':94370,'YKRY':94549,'YTNG':94376,\
     'YROM':94515,'YBCV':94510,'YLRE':94346,'YWTN':94342,'YBDV':95482, 'YLLE':95487, \
     'YWDH':94489,'YTGM':95492,'YSGE':94517,'YBMA':94332,'YCCY':94335,'YJLC':94337,\
     'YRMD':94341,'YHUG':94343,'YTMO':94336,'YTEE':94338,\
     'YBTL':94294,'YBMK':95367,'MKY':94367,'YBPN':94365,'YBHM':94368,\
     'YEML':94363,'YMRB':94397,'YCMT':94395,'YBCS':94287,'YBWP':94170,\
     'YHID':94174,'YLHR':94186,'YCKN':95283,'YGTN':94274,'YIFL':94280,'YMBA':95286,\
     'YCOE':94183,'YNTN':94266,\
     'YBKT':94260,'YCNY':94261,'YMTI':94254,'YKOW':94268,'YBSG':94171, 'YLZI':94188, \
     'YGLS':94461,'YKNT':94321,'YBAS':94326,'YAYE':94462,'YBYU':401476,'YJVN':401476, 'YPDN':94120,'YBTI':94122,'YSNB':94119,\
     'WPDL':99055,'YELD':95146,'YPGV':94150,'YGTE':94153, 'YTTI':94102,'YTST':95101,\
     'YHOO':94231,'YJAB':94137,'YMGD':95142,'YMGB':94140,'YMHU':94239,'YNGU':94106,\
     'YPKT':95111,'YPTN':94131,'YTNK':94238,'YYND':94328,'YTGT':95322,\
     'YARG':94217,'YBRY':99313,'YBWX':95304,'YBGD':94316,'YBRM':94203,'YCHK':99737,\
     'YPXM':96995,'YPCC':96996,'YCWA':99312,\
     'YDBY':95205,'YFTZ':94206,'YFDF':99736,'YHLC':94212,'YPKA':95307,'YPKU':94216,\
     'YWYM':95214,'YLBD':99206,'YTTI':95101,'YNWN':94317,\
     'YOLW':95305,'YPBO':94316,'YPPD':94312,'YCIN':94204,'YPLM':94302,'YSOL':99217,\
     'YTEF':94319,'YANG':99314,
     'YSSY':94767,'YSBK':95765,'YSRI':95753,'YSCN':94755,'YSHW':95761,'YSHL':95748,'YWLM':94776,
     'YPAD':94672,'YSCB':94926, 'YPPH':94610}

# Use Cape Flattery Sta Id 031213, WMO 94188 for Lizard Is


# avid to climate statistics file numbers on climate data online servers  BOM_ID in Callums FIle
avid_adams = \
    {'YBBN':'040842','YBAF':'040211','YAMB':'040004','YBSU':'040861', 'YBCG':'040717',\
     'YTWB':'041529','YBOK':'041359','YBWW':'041359',\
     'YKRY':'040922','YTNG':'039089','YGLA':'039326','YBRK':'039083',\
     'YBUD':'039128','YHBA':'040405','YMYB':'040126',\
     'YROM':'043091','YBCV':'044021','YLRE':'036031', 'YWTN':'4136',\
     'YBDV':'038026','YLLE':'045009','YWDH':'4135','YTGM':'045025','YSGE':'4110',\
     'YBMA':'029127','YCCY':'029141','YJLC':'029058', 'YRMD':'4100', 'YHUG':'030022',\
     'YTMO':'037034', 'YTEE':'037036',\
     'YBTL':'032040', 'YBMK':'033045', 'MKY':'033119', 'YBPN':'033247','YBHM':'033106',\
     'YEML':'4042', 'YMRB':'034038', 'YCMT':'4147','YBAS':'15590','YAYE':'15635',\
     'YPDN':'14015','YGLS':'13017',\
		 'YPGV':'14508','YGTE':'14518','YHOO':'14829','YJAB':'14198','YMGD':'14405','YMGB':'14404','YMHU':'14704','YKNT':15664,\
		 'YPKT':'14948','YPTN':'14932','YTNK':'15135','YARG':'2064','YBRY':'505053','YBWX':'5094',\
		 'YBGD':'505052','YBRM':'3003','YCHK':'505049','YPXM':'200790','YPCC':'200284','YCWA':'505051',\
		 'YDBY':'3032','YFTZ':'3093','YFDF':'505056','YHLC':'2012','YPKA':'4083','YPKU':'2056','YLBD':'503016',\
		 'YTST':'1020','YTTI':'1007','YNWN':'7176','YOLW':'5017','YPBO':'7185','YPPD':'4032','YCIN':'3080','YPLM':'5007',\
		 'YSOL':'505060','YTEF':'13030','YANG':'507501','YPCC':'200284','YPXM':'200790',\
       'YSSY':'066037','YSBK':'066137','YSRI':'067105','YSCN':'068192','YSHL':'068241'}


# avid to preci/town location mappings

avid_preci = \
    {'YBBN':'Brisbane','YBAF':'Oxley', 'YAMB':'Ipswich', 'YBSU':'Maroochydore', 'YBCG':'Coolangatta',\
     'YTWB':'Toowoomba','YBOK':'Oakey','YBWW':'Toowoomba',\
     'YKRY':'Kingaroy', 'YTNG':'Biloela',  'YGLA':'Gladstone','YBRK':'Rockhampton','YSMH':'Samuel Hill',\
     'YBUD':'Bundaberg','YHBA':'Hervey Bay','YMYB':'Maryborough',\
     'YROM':'Roma', 'YBCV':'Charleville', 'YLRE':'Longreach', 'YWTN':'Winton',\
     'YBDV':'Birdsville', 'YLLE':'Thargomindah', 'YWDH':'Windorah','YTGM':'Thargomindah','YSGE':'St George',\
     'YBMA':'Mount Isa', 'YCCY':'Cloncurry', 'YJLC':'Julia Creek', 'YRMD':'Richmond', 'YHUG':'Hughenden',\
     'YTMO':'Urandangi', 'YTEE':'Urandangi',\
     'YBTL':'Townsville', 'YBMK':'Mackay','YBPN':'Proserpine','YBHM':'Hamilton Island',\
     'YEML':'Emerald', 'YMRB':'Moranbah', 'YCMT':'Clermont',\
     'YBCS':'Cairns','YBWP':'Weipa','YHID':'Thursday Island','YLHR':'Lockhart River',\
     'YCKN':'Cooktown','YGTN':'Georgetown','YIFL':'Innisfail',\
     'YMBA':'Mareeba','YCOE':'Coen','YNTN':'Normanton','YBKT':'Burketown',\
     'YCNY':'Doomadgee','YMTI':'Mornington Island','YKOW':'Kowanyama' ,\
	   'YBAS':'Alice Springs','YAYE':'Yulara','YPDN':'Darwin','YBTI':'Wurrumiyanga','YSNB':'Pirlangimpi',\
     'YELD':'Ngayawili','YPGV':'Nhulunbuy Airport','YGTE':'Alyangula', 'YTGT':'Rabbit Flat',\
     'YHOO':'Lajamanu','YJAB':'Jabiru','YMGD':'Maningrida','YMGB':'Milingimbi','YMHU':'Borroloola','YNGU':'Ngukurr','YPKT':'Wadeye',\
     'YPTN':'Katherine','YTNK':'Tennant Creek','YYND':'Yuendumu','YGLS':'Docker River','YKNT':'Wulungurru',\
     'YARG':'Argyle','YBRY':'Barimunya','YBWX':'Barrow Island','YBGD': 'Paraburdoo', 'YWYM':'Wyndham', \
     'YBRM':'Broome','YCHK':'Paraburdoo','YPXM':'Christmas Island','YPCC':'Cocos Island','YCWA':'Paraburdoo',\
     'YDBY':'Derby','YFTZ':'Fitzroy Crossing','YFDF':'Paraburdoo',\
     'YHLC':'Halls Creek','YPKA':'Karratha','YPKU':'Kununurra','YLBD':'Lombadina',\
     'YTTI':'Kalumburu','YTST':'Kalumburu','YNWN':'Newman',\
     'YOLW':'Onslow','YPBO':'Paraburdoo','YPPD':'Port Hedland','YCIN':'Derby','YPLM':'Exmouth',\
     'YSOL':'Tom Price','YTEF':'Telfer','YANG':'Newman',\
     'YSSY':'Mascot','YSBK':'Liverpool','YSRI':'Richmond','YSCN':'Camden','YSHW':'Liverpool',\
     'YSHL':'Albion Park','YWLM':'Raymond Terrace',\
     'YSCB':'Canberra','YMML':'Melbourne','YPAD':'Adelaide','YPPH':'Perth'}


# avid to climate station numbers
# to read from Daily Weather Observations located at
#     http://www.bom.gov.au/climate/dwo/YYYYMM/html/IDCJDWxxxx.YYYYMM.shtml
# e.g http://www.bom.gov.au/climate/dwo/201603/html/IDCJDW4003.201603.shtml <--Archerfield April 2017
avid_climate = {'YBBN':'4020','YBAF':'4003', 'YAMB':'4002', 'YBSU':'4081', 'YBCG':'4036',\
              'YTWB':'4126','YBOK':'4093','YBWW':'4093',\
              'YKRY':'4069', 'YTNG':'4120',  'YGLA':'4049','YBRK':'4102',\
              'YBUD':'4021','YHBA':'4056','YMYB':'4082',\
              'YROM':'4104', 'YBCV':'4028', 'YLRE':'4074', 'YWTN':'4136',\
              'YBDV':'4011', 'YLLE':'4006', 'YWDH':'4135','YTGM':'4121','YSGE':'4110',\
              'YBMA':'4089', 'YCCY':'4031', 'YJLC':'4067', 'YRMD':'4100', 'YHUG':'4060',\
              'YTMO':'4123', 'YTEE':'4129',\
              'YBTL':'4128', 'YBMK':'4077', 'MKY':'4078', 'YBPN':'4096','YBHM':'4054',\
              'YEML':'4042', 'YMRB':'4087', 'YCMT':'4147' }



radarCoords = [{'locn':'Bowen','lat':19.88, 'long':148.08,'url':'http://www.bom.gov.au/products/IDR242.loop.shtml'},
	{'locn':'Brisbane (Mt Stapylton)','lat':27.72, 'long':153.24,  'url':'http://www.bom.gov.au/products/IDR662.loop.shtml'},
	{'locn':'Cairns','lat':-16.82, 'long':145.68,  'url':'http://www.bom.gov.au/products/IDR192.loop.shtml'},
    {'locn':'Emerald','lat':-23.55,'long':148.24, 'url':'http://www.bom.gov.au/products/IDR722.loop.shtml'},
	{'locn':'Mackay' ,'lat':-21.12,'long':149.22, 'url':'http://www.bom.gov.au/products/IDR222.loop.shtml'},
	{'locn':'Gladstone','lat':-23.86,'long':151.26, 'url':'http://www.bom.gov.au/products/IDR232.loop.shtml'},
	{'locn':'Gympie (Mt Kanigan)','lat':-25.96,'long':152.58, 'url':'http://www.bom.gov.au/products/IDR082.loop.shtml'},
	{'locn':'Longreach','lat':-23.43,'long':144.29, 'url':'http://www.bom.gov.au/products/IDR562.loop.shtml'},
	{'locn':'Marburg','lat':-27.61,'long':152.54, 'url':'http://www.bom.gov.au/products/IDR502.loop.shtml'},
	{'locn':'Mornington Island (Gulf of Carpentaria)','lat':-16.67,'long':139.17, 'url':'http://www.bom.gov.au/products/IDR362.loop.shtml'},
	{'locn':'Mount Isa','lat':-20.71,'long':139.56, 'url':'http://www.bom.gov.au/products/IDR752.loop.shtml'},
	{'locn':'Townsville (Hervey Range)','lat':-19.42,'long':146.55, 'url':'http://www.bom.gov.au/products/IDR732.loop.shtml'},
	{'locn':'Warrego','lat':-26.44,'long':147.35, 'url':'http://www.bom.gov.au/products/IDR672.loop.shtml'},
	{'locn':'Moree','lat':-29.5,'long':149.85, 'url':'http://www.bom.gov.au/products/IDR532.loop.shtml'},
	{'locn':'Grafton','lat':-29.62,'long':152.97, 'url':'http://www.bom.gov.au/products/IDR282.loop.shtml'},
	{'locn':'Weipa','lat':-12.67,'long':141.92, 'url':'http://www.bom.gov.au/products/IDR782.loop.shtml'},
	{'locn':'Willis Island','lat':16.29,'long':149.97, 'url':'http://www.bom.gov.au/products/IDR412.loop.shtml'},
	{'locn':'Broome','lat':-17.95,'long':122.23, 'url':'http://www.bom.gov.au/products/IDR172.loop.shtml'},
	{'locn':'Dampier','lat':-20.65,'long':116.69, 'url':'http://www.bom.gov.au/products/IDR152.loop.shtml'},
	{'locn':'Port Hedland','lat':-20.37,'long':118.63, 'url':'http://www.bom.gov.au/products/IDR162.loop.shtml'},
	{'locn':'Learmonth','lat':-22.10,'long':114.00, 'url':'http://www.bom.gov.au/products/IDR292.loop.shtml'},
	{'locn':'Carnarvon','lat':-24.88,'long':113.67, 'url':'http://www.bom.gov.au/products/IDR052.loop.shtml'},
	{'locn':'Giles','lat':-25.03,'long':128.30, 'url':'http://www.bom.gov.au/products/IDR442.loop.shtml'},
	{'locn':'Alice Springs','lat':-23.82,'long':133.90, 'url':'http://www.bom.gov.au/products/IDR252.loop.shtml'},
	{'locn':'Halls Creek','lat':-18.23,'long':127.66, 'url':'http://www.bom.gov.au/products/IDR392.loop.shtml'},
	{'locn':'Wyndham','lat':-15.45,'long':128.12, 'url':'http://www.bom.gov.au/products/IDR072.loop.shtml'},
	{'locn':'Katherine (Tindal)','lat':-14.51,'long':132.45, 'url':'http://www.bom.gov.au/products/IDR422.loop.shtml'},
	{'locn':'Darwin (Berrimah)','lat':-12.46,'long':130.93, 'url':'http://www.bom.gov.au/products/IDR632.loop.shtml'},
	{'locn':'Warruwi','lat':-11.65,'long':133.38, 'url':'http://www.bom.gov.au/products/IDR772.loop.shtml'},
	{'locn':'Sydney (Terry Hills)','lat':-33.40,'long':151.14, 'url':'http://www.bom.gov.au/products/IDR712.loop.shtml'},
    {'locn':'Canberra (Captains Flat)','lat':-35.5,'long':149.5, 'url':'http://www.bom.gov.au/products/IDR402.loop.shtml'},
    {'locn':'Melbourne','lat':-37.5,'long':144.5, 'url':'http://www.bom.gov.au/products/IDR022.loop.shtml'},
    {'locn':'Adelaide (Buckland Park) ','lat':-34.5,'long':138.5, 'url':'http://www.bom.gov.au/products/IDR642.loop.shtml'},
    {'locn':'Perth (Serpentine) ','lat':-32.2,'long':115.5, 'url':'http://www.bom.gov.au/products/IDR702.loop.shtml'}]


# These locations get a fully worded town forecast as well - can have more info than precis
towns_list = ['YBCS','YROM', 'YBCV','YBDV','YEML','YBRK', 'YGLA','YGDI','YHBA','YAMB','YLRE','YBMK',\
              'YBUD', 'YMYB','YBMA','YTWB','YBTL']


# weather columns in climate zone data files
wx_cols = ['PW',
 'PW1_int', 'PW1_desc', 'PW1_type',
 'PW2_int', 'PW2_desc', 'PW2_type',
 'PW3_int', 'PW3_desc', 'PW3_type',
 'RW1_desc', 'RW1_type',
 'RW2_desc', 'RW2_type',
 'RW3_desc', 'RW3_type']
# 'AWS_PW', 'AWS_PW15min', 'AWS_PW60min',  <-- these not avlble for brissy

'''
'PW1_int', 'PW1_desc', 'PW1_type',
'''
# Weather intensity (Light, mod, hvy) or proximity VC
# these are represeneted by integers 0 to 3
intensity = {0:'LT', 1:'MD', 2:'HV', 3:'VC'}

## two letter codes that form the prefix
## e.g in TSRA, 'TS' is the prefix/wx descriptor,
## 'RA' is suffix/weather type
wx_desc = {'MI':'shallow', 'BC':'patches', 'DR':'drifting',
           'BL':'blowing', 'SH':'showers', 'TS':'thunderstorm',
           'FZ':'freezing', 'PR':'partial'}

wx_type = {'DZ':'drizzle', 'RA':'rain','SN':'snow','SG':'snow grains',
'IC':'ice crystals','PL':'ice pellets','GR':'hail','GS':'small hail',
'BR':'mist','FG':'fog','FU':'smoke','VA':'vocanic ash','DU':'widespread dust',
'SA':'sand','HZ':'haze','PO':'dust devil','SQ':'squalls',
'FC':'funnel cloud','SS':'sandstorm','DS':'duststorm'}


# column names used to replace original climate-zone data file columns
cols =['hm', 'StNum', 'StName', 'Lat', 'Long', 'WMO_Num', 'AvID', 'Elevation_m', \
       'LST', 'UTC', 'M_type', 'pptn10min', 'pptn9am', 'T', 'Twb', 'Td', 'RH', \
       'VP', 'SVP', 'WS', 'WDir', 'MaxGust10min', 'CL1_amnt', 'CL1_type', 'CL1_ht',\
       'CL2_amnt', 'CL2_type', 'CL2_ht', 'CL3_amnt', 'CL3_type', 'CL3_ht', 'CL4_amnt',\
       'CL4_type', 'CL4_ht', 'Ceil1_amnt', 'Ceil1_ht', 'Ceil2_amnt', 'Ceil2_ht',\
       'Ceil3_amnt', 'Ceil3_ht','CeilSKCflag', 'vis', 'vis_min_dir', 'vis_aws', 'PW', 'PW1_int',\
       'PW1_desc', 'PW1_type', 'PW2_int', 'PW2_desc', 'PW2_type', 'PW3_int', 'PW3_desc', \
       'PW3_type', 'RW1_desc', 'RW1_type', 'RW2_desc', 'RW2_type', 'RW3_desc', 'RW3_type',\
       'AWS_PW', 'AWS_PW15min', 'AWS_PW60min', 'MSL', 'SLP', 'QNH', 'AWS_Flag', 'MSG',\
       'RMK', 'CAVOK_SKC_flag', 'RWY_ws_shear_flag', 'END']

# data column subset that we can treat as NUMERIC
cols_num = ['StNum', 'Lat', 'Long', 'WMO_Num',
       'Elevation_m',  'pptn10min', 'pptn9am', 'T', 'Twb',
       'Td', 'RH', 'VP', 'SVP', 'WS', 'WDir', 'MaxGust10min',
       'CL1_amnt', 'CL1_type', 'CL1_ht', 'CL2_amnt', 'CL2_type', 'CL2_ht',
       'CL3_amnt', 'CL3_type', 'CL3_ht', 'CL4_amnt', 'CL4_type', 'CL4_ht',
        'Ceil1_ht', 'Ceil2_ht', 'Ceil3_ht','CeilSKCflag',
        'vis', 'vis_min_dir', 'vis_aws',
        'PW', 'PW1_int','PW2_int', 'PW3_int', 'MSL', 'SLP', 'QNH',
       'AWS_Flag', 'CAVOK_SKC_flag', 'RWY_ws_shear_flag']

# data columns that we can safely treat as TEXT/STRINGS
cols_str = ['hm', 'StName','AvID','M_type','Ceil1_amnt','Ceil2_amnt', 'Ceil3_amnt',
            'PW1_desc', 'PW1_type','PW2_desc', 'PW2_type', 'PW3_desc','PW3_type',
            'RW1_desc', 'RW1_type', 'RW2_desc', 'RW2_type', 'RW3_desc','RW3_type',
            'AWS_PW', 'AWS_PW15min', 'AWS_PW60min','MSG', 'RMK']

cols_2_keep_auto_aws = \
['AvID','M_type','pptn10min', 'pptn9am', 'T', 'Twb',
'Td', 'RH', 'VP', 'SVP', 'WS', 'WDir', 'MaxGust10min','QNH',
'Ceil1_amnt','Ceil2_amnt', 'Ceil3_amnt',
'Ceil1_ht', 'Ceil2_ht', 'Ceil3_ht', 'CeilSKCflag','vis_aws',
'AWS_PW', 'AWS_PW15min', 'AWS_PW60min',
'AWS_Flag', 'CAVOK_SKC_flag', 'RWY_ws_shear_flag']
#'CL1_amnt', 'CL1_type', 'CL1_ht', 'CL2_amnt', 'CL2_type', 'CL2_ht',
#'CL3_amnt', 'CL3_type', 'CL3_ht', 'CL4_amnt', 'CL4_type', 'CL4_ht',
#'vis', 'vis_min_dir','PW',
#'PW1_int','PW2_int',  'PW3_int',
#'PW1_desc', 'PW1_type','PW2_desc', 'PW2_type', 'PW3_desc','PW3_type',
#'RW1_desc', 'RW1_type', 'RW2_desc', 'RW2_type', 'RW3_desc','RW3_type',
#'MSG', 'RMK']

cols_2_keep_manual_aws = \
['AvID','M_type','pptn10min', 'pptn9am', 'T', 'Twb',
'Td', 'RH', 'VP', 'SVP', 'WS', 'WDir', 'MaxGust10min','QNH',
'CL1_amnt', 'CL1_type', 'CL1_ht', 'CL2_amnt', 'CL2_type', 'CL2_ht',
'vis', 'vis_min_dir', 'PW',
'PW1_int','PW1_desc', 'PW1_type',
'PW2_int','PW2_desc', 'PW2_type',
'AWS_Flag', 'CAVOK_SKC_flag', 'RWY_ws_shear_flag']
#'Ceil1_amnt','Ceil2_amnt', 'Ceil3_amnt',
#'Ceil1_ht', 'Ceil2_ht', 'Ceil3_ht', 'CeilSKCflag','vis_aws',
#'AWS_PW', 'AWS_PW15min', 'AWS_PW60min',
#'CL3_amnt', 'CL3_type', 'CL3_ht', 'CL4_amnt', 'CL4_type', 'CL4_ht',
#'PW3_int', 'PW3_desc','PW3_type',
#'RW1_desc', 'RW1_type', 'RW2_desc', 'RW2_type', 'RW3_desc','RW3_type',
#'MSG', 'RMK']

# cols we want to keep, NB UTC datetime wud be in index, not in columns
cols_2_keep = \
['AvID', 'M_type', 'pptn10min', 'pptnSince9', 'T',
 'Td', 'RH', 'WS', 'WDir', 'MaxGust10min', 'QNH',
 'CL1_amnt', 'CL1_ht', 'CL2_amnt', 'CL2_ht', 'CL3_amnt', 'CL3_ht',
 'Ceil1_amnt','Ceil1_ht','Ceil2_amnt','Ceil2_ht', 'Ceil3_amnt', 'Ceil3_ht',
 'CeilSKCflag', 'vis', 'vis_min_dir','vis_aws',
 'PW', 'PW1_desc', 'PW1_type','PW2_desc', 'PW2_type','PW3_desc','PW3_type',
 'AWS_PW', 'AWS_PW15min', 'AWS_PW60min', 'AWS_Flag', 'CeilSKCflag']

'''
 tcz_col_names = ['AvID', 'date', 'M_type', 'pptn10min', 'pptnSince9', 'T', 'Td',
  'RH', 'WS', 'WDir', 'MaxGust10min', 'CL1_amnt', 'CL1_ht',
  'CL2_amnt', 'CL2_ht', 'CL3_amnt', 'CL3_ht', 'Ceil1_amnt',
  'Ceil1_ht', 'Ceil2_amnt', 'Ceil2_ht', 'Ceil3_amnt', 'Ceil3_ht',
  'CeilSKCflag', 'vis', 'vis_min_dir', 'vis_aws', 'PW', 'PW1_desc',
  'PW1_type', 'PW2_desc', 'PW2_type', 'PW3_desc', 'PW3_type',
  'AWS_PW', 'AWS_PW15min', 'AWS_PW60min', 'QNH', 'AWS_Flag']

### script to find/replace potential false matches in observations

(**already ran on the data files - repeat if grab new data**)

```
#!/bin/bash

#http://www.grymoire.com/unix/Sed.html#uh-10a
#- ignore case using '/I', be greedy 'g'
#- multiple find replace patterns using '-e'
#- sed -e 's/a/A/' -e 's/b/B/' <old >new

suffix="_new.txt"
for file_name in "$@"
do

name=`echo $file_name | cut -f1 -d'.'`

sed -e   's/knots/kt/Ig'  \
    -e   's/kts/kt/Ig'    \
    -e   's/gusts/gust/Ig'    \
    -e   's/reports/report/Ig'     \
    -e   's/remnants/remnant/Ig'   \
    -e   's/quadrants/quadrant/Ig' < $file_name > $name$suffix

done


Usage
%cd 'folder holding data files'

# find replace potential false matches in original datafiles
!sh replace_false_ts_matches.sh HM01X_Data_040842.txt HM01X_Data_040223.txt
'''

#############################################################
## Function to get read data from individual
## ClimateZone files and return properly formatted dataframe
#############################################################
def process_climate_zone_csv():

    df = pd.read_csv(file,
      parse_dates=[8,9],            # col 8,9 datetime like
      dayfirst=True,                # format like '31/10/2012 23:30' in file
      infer_datetime_format = True, # faster parsing 5-10x
      names=cols,                   # rename climatezone columns using cols list
      index_col=[9],                # make UTC datetime index
      low_memory=False,
      skiprows=1,                   # skip 1 line(s) at the start of the file.
      header=None )                 # don't use headers - we skipped header row!


    # convert these cols expected to be float/int to numeric
    # df[cols_num] = df[cols_num].astype(float, 'ignore')
    # too many errors with above vectorized approach

    for col in  cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # convert text data to string
    df[cols_str] = df[cols_str].astype(str)

    return (df)

tcz_file_map = {'YBBN':'040842', 'YBAF':'040211', 'YAMB':'040004',
           'YBSU':'040861', 'YBCG':'040717', 'YTWB':'041529',
           'YBOK':'041359', 'YBRK':'039083',
           'YPCC':'200284','YPXM':'200790',
           'YSSY':'066037','YSBK':'066137','YSRI':'067105',
           'YSCN':'068192','YSHL':'068241'}

def process_climate_zone_csv_2020(station:str='YBBN'):

    '''

    http://tcz.bom.gov.au:8889/tcz/anon/HM01X_D.HM01X_page
    Use this saved query: half_hourly_metar_data_extract
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    userid:vinorda
    pwd:usual
    ,40004,40211,40842,40717,40861,41359,41529,39083
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    '''

    #cur_dir="/home/bou/shared/stats-R/fog-project/tcz_data/HM01X_99999999_9852610"
    cur_dir = "/home/accounts/qdisplay/avguide/tmp/"
    #cur_dir='/home/bou/shared/stats-R/flask_projects/avguide/app/data'
    '''In the app,  cur_dir will come from environment config'''
    # data_file = f'HM01X_Data_{tcz_file_map[station]}.txt'
    data_file = os.path.join(cur_dir, f'HM01X_Data_{station}.txt')
    #file = os.path.join(cur_dir,'app','data',data_file)
    #file = os.path.join(cur_dir,data_file)

    print(f'\nProcessing aviation location {station}, file={data_file}')
    use_tcz_cols =[ 5,  7,  8,  9, 10, 11, 13, 14, 17, 18, 19, 20, 22, 23, 25, 26, 28,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 47, 48, 50, 51,
    58, 59, 60, 63, 64]

    tcz_col_names = ['AvID', 'date', 'M_type', 'pptn10min', 'pptnSince9', 'T', 'Td',
    'RH', 'WS', 'WDir', 'MaxGust10min', 'CL1_amnt', 'CL1_ht',
    'CL2_amnt', 'CL2_ht', 'CL3_amnt', 'CL3_ht', 'Ceil1_amnt',
    'Ceil1_ht', 'Ceil2_amnt', 'Ceil2_ht', 'Ceil3_amnt', 'Ceil3_ht',
    'CeilSKCflag', 'vis', 'vis_min_dir', 'vis_aws', 'PW', 'PW1_desc',
    'PW1_type', 'PW2_desc', 'PW2_type', 'PW3_desc', 'PW3_type',
    'AWS_PW', 'AWS_PW15min', 'AWS_PW60min', 'QNH', 'AWS_Flag']

    cols_num = ['pptn10min', 'pptnSince9', 'T','Td', 'RH','WS', 'WDir', 'MaxGust10min',
    'CL1_amnt', 'CL1_ht', 'CL2_amnt', 'CL2_ht','CL3_amnt','CL3_ht','Ceil1_ht', 'Ceil2_ht',
    'Ceil3_ht','vis', 'vis_min_dir', 'vis_aws','PW', 'QNH', 'AWS_Flag',
    'CeilSKCflag']

    cols_str = ['AvID','M_type','Ceil1_amnt','Ceil2_amnt', 'Ceil3_amnt',
    'PW1_desc', 'PW1_type','PW2_desc', 'PW2_type', 'PW3_desc','PW3_type',
    'AWS_PW', 'AWS_PW15min', 'AWS_PW60min','CeilSKCflag']

    df = pd.read_csv(data_file,
    parse_dates=[7],            # col 8,9 datetime like
    dayfirst=True,                # format like '31/10/2012 23:30' in file
    infer_datetime_format = True, # faster parsing 5-10x
    usecols=use_tcz_cols,
    names=tcz_col_names,          # rename climatezone columns using cols list
    index_col=['date'],           # make UTC datetime index
    low_memory=False,
    skiprows=1,                   # skip 1 line(s) at the start of the file.
    header=None )                 # don't use headers - we skipped header row!

    # convert these cols expected to be float/int to numeric
    # df[cols_num] = df[cols_num].astype(float, 'ignore')
    # too many errors with above vectorized approach

    for col in  cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # convert text data to string
    df[cols_str] = df[cols_str].astype(str)

    df.index = pd.to_datetime(df.index)

    '''  Created new aws data Sept 2020
    We now do not write data file until merged with gpats
    cur_dir = '/home/bou/shared/stats-R/flask_projects/avguide'

    with open(
        os.path.join(cur_dir,'app','data',station+'_aws.pkl') , 'wb') as f:
        pickle.dump(df, f)
    '''
    return (df)

'''
#Run again if update data
>>> import utility_functions_sep2018 as bous
>>> import pandas as pd
>>> tcz_file_map = {'YBBN':'040842', 'YBAF':'040211', 'YAMB':'040004',
...                 'YBSU':'040861', 'YBCG':'040717', 'YTWB':'041529',
...                 'YBOK':'041359', 'YBRK':'039083',
...                 'YPCC':'200284','YPXM':'200790',
...                 'YSSY':'066037','YSBK':'066137','YSRI':'067105',
...                 'YSCN':'068192','YSHL':'068241'}

# read csv, extract relevant columns, do appropriate processing and then store picklised data on system
>>> for station,file in tcz_file_map.items():
...     print(station,file)
...     bous.process_climate_zone_csv_2020(station)

YSBK 066137

Processing aviation location YSBK, file=/home/bou/shared/stats-R/fog-project/tcz_data/HM01X_99999999_9852610/HM01X_Data_066137.txt
Processing aviation location YSCN, file=/home/bou/shared/stats-R/fog-project/tcz_data/HM01X_99999999_9852610/HM01X_Data_068192.txt
...

Handling old aws site data for YBBN
-------------------------------------
ybbn_old = process_climate_zone_csv('~/data/HM01X_Data_040223_new.txt')
ybbn_new = process_climate_zone_csv('~/data/HM01X_Data_040842_new.txt')

# Grab data from both old and new YBBN sites
# Merge old and new site data into single file

ybbn_old['WS'] = ybbn_old['WS']/1.85198479488
ybbn_old['MaxGust10min'] = ybbn_old['MaxGust10min']/1.85198479488


ybbn_old = ybbn_old\
    .loc[:'2000-02-14 02:30:00',cols_2_keep]
ybbn_new = ybbn_new\
    .loc['2000-02-14 03:00:00':,cols_2_keep]

df = pd.concat(
    [ybbn_old, ybbn_new],
    axis=0,
    join='outer',
    ignore_index=False )

df.to_csv('tmp/data/Brisbane_aws_Jan1985-Jan2018.csv')

import  pickle
with open('~/data/Brisbane_aws_Jan1985-Jan2018.pkl', 'wb') as f:
    pickle.dump(df, f)

'''

####################################################
############ READ  GPATS DATA FILE #################
####################################################
'''
>>> cur_dir='/home/bou/shared/stats-R/flask_projects/avguide/app/data/'
>>> g = bous.get_gpats_data(cur_dir,'YSSY')
Reading YSSY gpats file /home/bou/shared/stats-R/flask_projects/avguide/gpats/YSSY_10NM.csv
>>> g.tail()
                      LATITUDE   LONGITUDE  AMP
TM                                             
2020-09-25 11:50:00 -27.549110  153.173250    1
2020-09-25 11:57:00 -27.529860  153.190630    1
2020-09-25 12:20:00 -27.305605  153.025925    2


# gpats datetime stamps have miscrosecond precisions
   2008-03-28 04:37:06.546000
   YYYY-MM-DD HH:MM:SS.uuuuuu
# This is NOT COMPATIBLE WITH AWS DATA datetime stamps
# which has HH:MM resolution
# so we drop it right after read.csv()
# NB We could have also resampled to seconds
'''

def get_gpats_data(cur_dir:str="./gpats_data/",sta:str="YBBN")->pd.DataFrame:
    """[summary]
    Args:
        cur_dir (str, optional): [FOlder that stores gpat data]. Defaults to "./gpats_data/".
        sta (str, optional): [Aviation location]. Defaults to "YBBN".
    Returns:
        pd.DataFrame: [description]
    """
    # join is smart so cur_dir can be like ./gpats  or ./gpats/
    gpats_file = os.path.join(cur_dir, f'gpats_{sta}_10NM.csv')
    print("Reading {} gpats file {}".format(sta, gpats_file))

    gpats = pd.read_csv(gpats_file,parse_dates=True, index_col='TM').\
            resample('1min').\
            agg(dict(LATITUDE='mean', LONGITUDE='mean', AMP='count')).\
            dropna()
    ''' PREVIOUS VER of CODE
    gpats = pd.read_csv(gpats_file,parse_dates=True, index_col='TM')
    has HH:MM:SS resolution, mostly HH:MM so we trim it
    We have non-standard datetime, use pd.to_datetime after pd.read_csv
    apply custom string format to drops higher precision microseconds'''
    # gpats_new_index = gpats.index.strftime('%Y:%m:%d %H:%M:%S')
    '''
    convert string/object dateime back to datetime type
    and use that as new index for gpats df'''
    # gpats.index = pd.to_datetime(gpats_new_index,
    #                             format='%Y:%m:%d %H:%M:%S',
    #                             errors='coerce')

    return (gpats)


###################################################################
''' Simple way to get storm dates for location with observer
    check present weather groups reported by observer
    input - original climate zone aws data file
          - gpats file for aws station
    out  - list of days we had storms at station    '''

def get_storm_dates(gpats:pd.DataFrame,df:pd.DataFrame):
    """[summary]

    Args:
        gpats (pd.DataFrame): [description]
        df (pd.DataFrame): [description]

    Returns:
        [pd.Datetime]: [List of dates when we had storms at station]
    """

    #storm_dates = []
    storm_dates_pw = []
    storm_dates_gpats=[]

    sta = str(df.iloc[-1]['AvID']).strip()
    print("Getting storm dates for:", sta,"from aws metar/speci and gpats data.")

    #gpats = get_gpats_data(cur_dir + 'gpats/', sta)
    #print("Reading gpats file:",(cur_dir + 'gpats/', sta))

    gpats_ts_stats = get_gpats_start_end_duration(gpats)
    storm_dates_gpats = gpats_ts_stats.index.unique()
    print("Storm dates derived from gpats data for {} = {}"\
          .format(sta, len(storm_dates_gpats)))

    #storm_dates = storm_dates_gpats
    '''
    If manual station, check observers Present Weather groups
    AWS (Automatic Weather Station) flag
    0 Manned    1 Automatic     2 Hybrid '''
    # if (df.iloc[-1]['AWS_Flag'] == 2): #tis wud not alwys work!!
    hybrid_sta_list = ['YBBN','YAMB','YBOK','YBRK','YTBL','YBCS','YSSY','YWLM','YPDN','YPTN','YBTL','YPCC','YPXM']
    if sta in hybrid_sta_list:
        # build dict key:val, where key is wx-codes and value is wx-desc
        pw = {91: 'TS', 92: 'TS', 93: 'TS', 94: 'TS', 95: 'TS', \
          96: 'TSGS', 99: 'TSGR', 97: '+TS', 98: 'TSDU', \
          17: 'Thunder', 13: 'Lightning', 29: 'Recent TS', \
          27: 'GSGR', 89: 'SHGS', 90: 'SHGR'}

        '''NB: Hail falls as SH from CB only, generally with TS activity
        Hail GR >=5mm diameter (GS<=5mm- small hail/snow pellets)        '''

        dat = df.copy()  # make copy so as not to corrupt orignal df

        # for the other reported present weatqher groups
        dat['pw1'] = str_join(dat, '', 'PW1_desc', 'PW1_type')
        dat['pw2'] = str_join(dat, '', 'PW2_desc', 'PW2_type')
        dat['pw3'] = str_join(dat, '', 'PW3_desc', 'PW3_type')
        # We no longer processing RW grops !!!
        #dat['rw1'] = str_join(dat, '', 'RW1_desc', 'RW1_type')
        #dat['rw2'] = str_join(dat, '', 'RW2_desc', 'RW2_type')
        #dat['rw3'] = str_join(dat, '', 'RW3_desc', 'RW3_type')

        # join groups using ':'
        dat['pw1to3'] = str_join(dat, ':', 'pw1', 'pw2', 'pw3')
        #dat['rw1to3'] = str_join(dat, ':', 'rw1', 'rw2', 'rw3')

        # join PWs to RWs using '|'
        dat['pw_rw'] = str_join(dat, '|', 'pw1to3') #, 'rw1to3')

        # get TS start and end times and duration
        #wx_cols = ['T', 'Td', 'RH', 'WS', 'WDIR', 'vis', 'vis_aws',
        #           'PW', 'MaxGust10min', 'pptn10min', 'QNH']

        pw_ts_mask = dat['PW'].isin(list(pw.keys()))
        pwrw_ts_mask = dat['pw_rw'].str.contains(r'TS')
        wx_ts_mask = pw_ts_mask | pwrw_ts_mask

        wx_ts_specials = dat.loc[wx_ts_mask]
        ts_start_end = get_ts_start_end_duration(wx_ts_specials)
        storm_dates_pw = ts_start_end.index.unique()
        print("Storm dates derived from observer reported PW groups for {} = {}" \
              .format(sta, len(storm_dates_pw)))

        # WE could also do fog same way
        # pwrw_fg_mask = dat['pw_rw'].str.contains(r'FG')
        '''# get FOG stats -> start and end times and duration
        wx_fg_specials = dat.loc[pwrw_fg_mask,wx_cols]
        fg_start_end = get_ts_start_end_duration(wx_fg_specials)
        fg_vis1km = fg_start_end[fg_start_end.min_vis < 1]'''

    print("Total TS dates found for {} = {}" \
              .format(sta,
                len(set(storm_dates_pw).union(set(storm_dates_gpats))), # union two sets
                len(np.unique(list(set().union(storm_dates_pw,storm_dates_gpats))))))   # union two lists

    '''A python set is a dictionary that contains only keys (and no values).
    Dictionary keys are, by definition, unique. Duplicate items are weeded out automatically'''
    return  list(set(storm_dates_pw).union(set(storm_dates_gpats)))
    # return (np.unique(storm_dates_pw.union(storm_dates_gpats)))



####################################################
########## TS START/END/DURATION FM GPATS###########
####################################################

def get_gpats_start_end_duration(gpat:pd.DataFrame)->pd.DataFrame:

    import numpy as np

    '''define multiple aggregations per group
    use the 'AMP' column for counting strikes
    use 'Time' col to grab first and last gpats for a given day
    '''
    gpats = gpat.copy()
    gpats['Time'] = gpats.index

    aggregator = {'AMP' : {'gpats_cnt':'count'}, 'Time' : ['first','last']}
    daily = gpats.resample('D').apply(aggregator).dropna()
    # NB using a dict with renaming is deprecated
    # and will be removed in a future version!!

    tmp = daily['Time']
    daily.loc[:, ('Time','duration')] = round(\
        (tmp['last'] - tmp['first'])/np.timedelta64(1, 'h') , 1)

    # drop outer-most column index level 0 ['CNT','Time']
    daily.columns = daily.columns.droplevel(0)

    # get rid of zero duration events
    # daily = daily[daily['duration'] > '00:00:00']
    daily = daily[daily['duration'] > 0]

    return( daily[['gpats_cnt','duration','first','last']])



################################################################
'''Load climcate zone data file for station and combine
with 1min resampled gpats counts for same station.
adds any_ts flag to aws data for dates when had TS
saves the merged aws/gpats data file as pickled obj

for stations without manual obs, unless TS has caused a SPECI
(vis/ceil reductions or wind gust),no SPECI will be generated.
In this case we use gpats observation and flag the aws obs closest
(in time) to the gpats record with gpats['AMP'] count.
non zero values of this count would indicate presence of lightning.

We could resample gpats to 30min to make it better align
with 1/2 hrly aws, but this will miss a lot of non-routine
species
resample to 1min alighns better to non-routine species
left merge to retain all non-routine SPECI aws

input: sta - aviation id of station e.g 'YBBN'
       aws_file e.g 'HM01X_Data_040211_YBAF.txt'

'''
###############################################################

def merge_aws_gpats_data(sta):

    cur_dir = "/home/accounts/qdisplay/avguide/tmp/"
    #cur_dir='/home/bou/shared/stats-R/flask_projects/avguide/app/data/'
    '''In the app,  cur_dir will come from environment config
    gpats fil ename like       --> gpats_YPXM_10NM.csv
    tcz climate zone data file --> HM01X_Data_YPXM.txt'''
    # gpats_file = f'gpats_{sta}_10NM.csv'
    # file = os.path.join(cur_dir,'app','data',data_file)
    gpats_file = os.path.join(cur_dir, f'gpats_{sta}_10NM.csv')
    tcz_file =   os.path.join(cur_dir, f'HM01X_Data_{sta}.txt')

    print(f'\nProcessing sta={sta},\nClimate Zone data file:{tcz_file}",\
        \nGpats file: {gpats_file}')

    # load climate zone data file, except for Brisbane
    #if sta is 'YBBN':
    #    df = pickle.load(open(os.path.join(cur_dir,'tcz', aws_file), 'rb'))
    #else:
    #df = process_climate_zone_csv(cur_dir+'tcz/'+aws_file)
    df = process_climate_zone_csv_2020(sta)
    #print(df.head(1))
    #print(df.tail(1))

    # we check both aws metar/speci and gpats for ts days now
    # this not just checks fo gpats lightning but also observer PW groups
    gpats =    get_gpats_data(cur_dir, sta)
    #print(gpats.head(1))
    #print(gpats.tail(1))

    ts_dates = get_storm_dates(gpats,df)

    # print(len(ts_dates), ts_dates)
    df = df[cols_2_keep]

    # FLAG AWS OBS WITH TS FLAG IF TS ON THAT DATE
    df['date'] = pd.to_datetime(df.index.date)
    df['any_ts'] = df['date'].isin(ts_dates)

    '''for stations without manual obs, unless TS has caused a SPECI
    (vis/ceil reductions or wind gust),no SPECI will be generated.
    In this case we use gpats observation and flag the aws obs closest
    (in time) to the gpats record with gpats['AMP'] count.
    non zero values of this count would indicate presence of lightning.

    fn get_gpats_data() expects gpats folder and station avID
    def get_gpats_data(gpats_dir,sta):
      gpats_file = gpats_dir+sta+'_gpats_10NM.csv'

    # gpats.resample('D')['AMP'].count() <- daily lightning counts
    '''
    # RESAMPLE GPATS TO 1MIN LIGHTNING COUNTS AND MERGE WITH CLOSEST AWS OBS
    # gpats = get_gpats_data(cur_dir, sta)
    df = pd.merge( left=df,
                  right=gpats.resample('30min')['AMP'].count(),
                  left_index=True, right_index=True,how='left')
    df['AMP'] = df['AMP'].fillna(value=0)   # replace NaNs with 0

    '''potential data redundancy 'any_ts' flags all obs for day with TS status
    'AMP' lightning count assigned to aws obs if gpats around time of obs'''
    file = os.path.join(cur_dir, f'{sta}_aws.pkl')
    with open(file, 'wb') as f:
        pickle.dump(df, f)


##################################################################
'''
Get fog dates from SFC_DAYS table in ADAMS

Add fog flag in AWS obs from climate_zone

SELECT TO_CHAR(LSD, 'yyyy-mm-dd') AS Day, count(distinct decode(fog_flag,'Y',lsd))
FROM SFC_DAYS WHERE
LSD > TO_DATE('{start}', 'yyyy-mm-dd') AND LSD <= TO_DATE('{end}', 'yyyy-mm-dd')
AND STN_NUM={station}
GROUP BY TO_CHAR(LSD, 'yyyy-mm-dd')
'''


def update_aws_fog_flag(sta):

    # get fog dates from sfc_days table in ADAMS
    fg_dates = get_fog_dates(sta)

    # FLAG AWS OBS WITH TS FLAG IF TS ON THAT DATE
    df = pickle.load(
            open(os.path.join('app','data',sta+'_aws.pkl'), 'rb'))
    print("update_aws_fog_flag- Brisbane data b4 add fog flag\n", df.tail())
    df['date'] = pd.to_datetime(df.index.date)
    df['fogflag'] = df['date'].isin(fg_dates)
    print("update_aws_fog_flag- Brisbane data after add fog flag\n", df.tail())
    '''potential data redundancy 'fogflag' flags all obs with FG status'''

    with open(os.path.join('app','data',sta+'_aws1.pkl'), 'wb') as f:
        pickle.dump(df, f)



# Function to concatenate, join many cols together
# to joing 2 cols we could just do
# df[col1].str.cat(df[col2])
# but col1 or col2 could be numeric, so need .astype(str) on the fly conversion
# else get errors

# https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-dataframe-in-pandas-python
def str_join(df, sep, *cols):
    from functools import reduce
    return reduce(
        lambda x, y: x.astype(str).str.cat(y.astype(str), sep=sep),\
        [df[col] for col in cols]
    )


###################################################################

################################################################
'''Extract daily 23Z F160 sonde files for given station from
aifsa-sa archives and save as individual text files for each day
Uses Hanks extract_skewt_from_adam.pl interface
Downloads daily 2300Z Brisbane sonde as text files

Individual sonde files have this form
---------------------------------------
[Header]
aifstime[18]="201802122300"
stationname[30]="Brisbane Ap"
stationnumber=040842
levels=76
fields=5
w_units=1
[$]

[Trace]
Pres,Geop,Temp,Dewp,Dir,Spd,AbsHum
1010.0,-9999.0,27.0,24.0,40.0,15.4,-9999.0
1000.0,-9999.0,25.9,23.4,50.0,23.0,-9999.0
979.0,-9999.0,24.9,22.8,65.0,18.0,-9999.0
978.0,-9999.0,-9999.0,-9999.0,65.0,17.4,-9999.0
958.0,-9999.0,25.8,19.9,55.0,13.2,-9999.0
950.0,-9999.0,25.3,19.3,40.0,11.8,-9999.0
--------------------------------------------
# len(pd.date_range(start='2000-Feb-01', end='2018-Feb-13', freq='D'))
# 6588 days of 23 sonde data '''
###############################################################

def batch_download_F160_hanks(station:str="040842",start_date='None',end_date='None',hour='1700',exact='on'):

    # print("Start date",start_date)
    # if no date supplied grab todays sonde file
    if start_date == 'None':
        start_date = pd.datetime.today().strftime("%Y-%m-%d")
        end_date = start_date


    cur_dir = "/home/accounts/vinorda/Downloads/"
    f160_url = 'http://aifs-sa.bom.gov.au/cgi-bin/extract_skewt_from_adam.pl'
    #dates = pd.date_range(start='2000-Feb-01', end='2018-Feb-13', freq='D')
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    print("Fetching sonde data for {} from {} to {}"\
        .format(station,start_date, end_date))

    for day in dates:
        day, month, year = day.day,day.month,day.year
        payload = {'d':day,'m':month,'y':year,'h':hour,'stn': station,'exact':exact,\
            'plot':'go','prev':'None','ascii':'on','ascii2':'off','reverse':'','crap':9558}
        # print(payload['stn'])
        # print(day.day,day.month,day.year)
        '''?plot=go&d=1&m=1&y=2010&h=2300&stn=040842&prev=None&exact=&ascii=on&ascii2=off&reverse=&crap=9558'''

        f160_response = requests.get(f160_url, params=payload)

        print (f160_response.url)  #check if url formed correctly

        if (f160_response.status_code == requests.codes.ok):
            '''
            print ("Found file resource")
            print (f160_response.headers.get('content-type'),"\n")'''

            '''build file name as string then save response file '''
            f160_file = cur_dir+'f160_'+str(hour)+'/stn'+str(payload['stn'])+'_'+\
            str(year)+'-'+str(month)+'-'+str(day)+'.txt'
            with open(f160_file, 'wb') as f:
                f.write(f160_response.content)

            # print(f160_response.content)


#########################################################################
## Approximate 500hpa data when no standard level 500hpa
'''
Not all daily sonde data have Pressure level exactly == 500,
99% have, 1% that don't cause lotta issues..

This makes it difficult to extract 500 level using simple
### `feb_2018.loc[feb_2018['Pres'] == 500].sort_index()`
Queries like this
### `feb_2018[(feb_2018['Pres'] > 499) & (feb_2018['Pres'] < 501)]`
### `pandas.Series.between(left, right, inclusive=True)`
### ` feb_2018.loc[feb_2018['Pres'].between(499,501,True)].sort_index()`
return too many rows

How do we only filter row that has Pressure value closest to 500.0 if not 500.0

https://www.science-emergence.com/Articles/Find-nearest-value-
    and-the-index-in-array-with-python-and-numpy/
https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

If you want the index of the element of array (array)
nearest to the the given number (num)

### `nearest_idx = n.where(abs(array-num)==abs(array-num).min())[0] `

Access the element of array(array) nearest to the given number (num)
### `nearest_val = array[abs(array-num)==abs(array-num).min()] `

for each days sonde data we want to pick out row where the
pressure value is closest to 500.0

we want row where we have smallest difference between pressure value and 500
we don't want row index but actual pressure value, so we can then search
using this value in the daily data and grab just ONE row cloest to 500 hpa

where p_hPa = dat['Pres'] (series containing pressure levels)
- `np.abs(p_hPa-500.0)` finds dist from 500.0 for all p values
- `np.abs(p_hPa-500.0).min()` is lowest when p_hPa almost 500.0
- `np.abs(p_hPa-500.0) == np.abs(p_hPa-500.0).min()`
   is False for all rows except row with pressure value closest to 500.0
   Guranteed to have True for at most one row. WHAT ABOUT TIES??
- `p_hPa[boolean series]` where boolean series has one True value
- `p_hPa[np.abs(p_hPa-500.0) == np.abs(p_hPa-500.0).min()]`
   filters using boolean indexing the pressure value clost to 500.0

'''


def closest_900h(dat):
    if dat.empty:
        print('DataFrame is empty!')
        return # exit function
    else:
        p_hPa = dat['Pres']
        p_level = \
            p_hPa[np.abs(p_hPa-910.0) == (np.abs(p_hPa-910.0).min())][0]
    return (dat[dat['Pres'] == float(p_level)])



def closest_850h(dat):
    if dat.empty:
        print('DataFrame is empty!')
        return # exit function
    else:
        p_hPa = dat['Pres']
        p_level = \
            p_hPa[np.abs(p_hPa-850.0) == (np.abs(p_hPa-850.0).min())][0]
    return (dat[dat['Pres'] == float(p_level)])


def closest_700h(dat):
    if dat.empty:
        print('DataFrame is empty!')
        return # exit function
    else:
        p_hPa = dat['Pres']
        p_level = \
            p_hPa[np.abs(p_hPa-700.0) == (np.abs(p_hPa-700.0).min())][0]
    return (dat[dat['Pres'] == float(p_level)])


def closest_500h(dat):
    if dat.empty:
        print('DataFrame is empty!')
        return # exit function
    else:
        p_hPa = dat['Pres']
        p_level = \
            p_hPa[np.abs(p_hPa-500.0) == (np.abs(p_hPa-500.0).min())][0]
    return (dat[dat['Pres'] == float(p_level)])


'''
## Approximate 900hpa data when no standard level 500hpa
def closest_level(dat):
    if dat.empty:
        print('DataFrame is empty!')
        return  # exit function
    else:
        p_hPa = dat['Pres']
        p_900 = p_hPa[np.abs(p_hPa - 900.0) == np.abs(p_hPa - 900.0).min()]
        p_850 = p_hPa[np.abs(p_hPa - 850.0) == np.abs(p_hPa - 850.0).min()]
        p_700 = p_hPa[np.abs(p_hPa - 700.0) == np.abs(p_hPa - 700.0).min()]
        p_500 = p_hPa[np.abs(p_hPa - 500.0) == np.abs(p_hPa - 500.0).min()]

    return (pd.concat([p_900,p_850,p_700,p_500], axis=1))
'''
######################################################
## Batch process sonde txt files
## downloaded using Hanks extract_skewt_from_adam.pl
'''some files don't have any data
   files > 215KB are OK THRU trial/error

# largest 2 files - see pipe to head
# grep -v '^d' <--exclude directories  grep '^-' only shows regular files
# -k 5 means sort using values in 5th column - this lists file sizes
# -rn
# -n, --numeric-sort: compare according to string numerical value
# -r, --reverse: reverse the result of comparisons

!ls -lR /home/bou/windows-shared/data/f160 | grep '^-' | sort -k 5 -rn | head -n 2

# smallest files - se pipe to tail
!ls -lR /home/bou/windows-shared/data/f160 | grep '^-' | sort -k 5 -rn | tail -n 14

# To get full pat of filenames pipe output of find to sort
# Note we sort on colum k=7 now
!find /home/bou/windows-shared/data/f160 -type f -ls | sort -rn -k7 | tail -n 1

'''

#####################################################
## WARNING : IF U CHANGE f160 FOLDER - FEW THINGS BREAK!!!

def batch_process_F160_hanks(station:str='YBBN',time:str='0500'):
    """[Read daily sonde data .txt files from a manually specified folder
    and assemble data for main standard levels and some derived quantities
    like 85 to 500 lapse rates, CAPE, LI, TOTA, DLM Steering etc]

    Args:
        station (str, optional): [F160 Radio-sonde station - 4 chars wide]. Defaults to 'YBBN'.
        time (str, optional): [Sonde release time]. Defaults to '0500'.
    """
    import os
    from glob import glob
    import pickle

    cur_dir = "/home/accounts/vinorda/Downloads/"   # ONLY FOR STANDALONE CALLS
    print("f160 data dir = ", cur_dir+station+'_f160_'+time+'/')
    filenames = glob(cur_dir+station+'_f160_'+time+'/stn*txt')
    print(len(filenames), filenames[-5:])
    dataframes = []
    f_dates=[]

    # dataframes = [pd.read_csv(f) for f in filenames]

    for f in filenames:
        '''some files don't have any data
        files > 215KB are OK THRU trial/error
        '''

        # print('file size',os.path.getsize(f))

        try:
            if os.path.getsize(f) > 215:

                # Non empty file exists, extract date from file name
                # NB IF U CHANGE f160 FOLDER - CAN'T GET DATES!!!
                # cur_dir = '/home/accounts/vinorda/sr-ask-11966/data/' split(7)!!

                print(f.split('/')[6].split('.')[0][10:])
                f_dates.append(f.split('/')[6].split('.')[0][10:])
                dat = pd.read_csv(f, skiprows=10, skip_blank_lines=True)

                # drop these 2 cols - have no actual data
                dat.drop(['Geop', 'AbsHum'], axis=1,inplace=True)

                # drop rows with 2 or more NAN/missing
                # dat.dropna(axis=0, thresh=2,inplace=True)

                # force convert all data to numeric
                for col in  dat.columns:
                    dat[col] = pd.to_numeric(dat[col], errors='coerce')

                dataframes.append(dat)

            else:
                # If file is empty - skip
                print("Empty file {}!!".format(f))
                continue # go to next file
        except OSError as e:
            # File does not exists or is non accessible
            print("What da ..Empty file {}".format(f))
        finally:
            print("Processing file {}".format(f))

    # concat/join all daily data into 1 big file
    df = pd.concat(dataframes,axis=0, keys=f_dates)

    # find replace all missing values indicated by -9999 to NaN
    # https://machinelearningmastery.com/handle-missing-data-python/
    df.replace(-9999,np.NaN, inplace=True)

    # drop integer row ids that form inner index
    # n make index datetime index
    df.index = df.index.droplevel(1)
    df.index = pd.DatetimeIndex(df.index)

    # read sonde data and use 1st row as proxy for sfc conditions
    # and 850/500 data to get env lapse rates and upper temps

    sfc_proxy = df.resample('D').first()

    lev500 = df.resample('D')\
                .apply(closest_500h)\
                .reset_index(level=0,drop=True).sort_index()
    lev700 = df.resample('D') \
                .apply(closest_700h) \
                .reset_index(level=0, drop=True).sort_index()
    lev850 = df.resample('D')\
                .apply(closest_850h)\
                .reset_index(level=0,drop=True).sort_index()
    lev900 = df.resample('D') \
                .apply(closest_900h) \
                .reset_index(level=0, drop=True).sort_index()

    sfc_500_sonde = pd.concat([sfc_proxy, lev900,lev850,lev700,lev500], axis=1)
    '''
    p_levels = df.resample('D')\
                .apply(closest_level)\
                .reset_index(level=0,drop=True).sort_index()
    sfc_500_sonde = pd.concat([sfc_proxy, p_levels], axis=1) '''
    # sfc_500_sonde.to_csv(cur_dir+'f160/sonde_data_hanks_2000to2018_june10.csv')
    col_names=['sfc_P','sfc_T','sfc_Td','sfc_wdir','sfc_wspd',
    'P910','T910','Td910','900_wdir','900_WS',
    'P850','T850','Td850','850_wdir','850_WS',
    'P700','T700','Td700','700_wdir','700_WS',
    'P500','T500','Td500','500_wdir','500_WS']
    sfc_500_sonde.columns = col_names  #rename col names
    sfc_500_sonde['tmp_rate850_500'] = sfc_500_sonde['T850']-sfc_500_sonde['T500'] # get lapse rates

    #cur_dir = '/home/bou/shared/stats-R/flask_projects/avguide'
    #with open(
    #    os.path.join(cur_dir,'app','data',station+'_sonde_'+time+'_aws.pkl') , 'wb') as f:
    #    pickle.dump(df, f)
    with open(
        os.path.join(cur_dir+station+'_sonde_'+time+'_aws.pkl') , 'wb') as f:
        pickle.dump(sfc_500_sonde, f)

    # sfc_500_sonde.to_csv(cur_dir+'f160_0300/YSSY_sonde03z_2000to2020.csv')
    return(sfc_500_sonde)


def get_sounding_data(station:str='YBBN',time:str='2300',level:str=None)->pd.DataFrame:
    """
    [Grab sounding data for station - obseleted #############]
    Args:
        station (str, optional): [description]. Defaults to 'YBBN'.
        level (str, optional): [description]. Defaults to None.
    Returns:
        pd.DataFrame: [description]
    """
    # cur_dir = '/home/bou/Downloads/'
    cur_dir = '/home/bou/shared/stats-R/flask_projects/avguide/app/data'
    # cur_dir = "/home/accounts/qdisplay/avguide/app/data"
    col_names=['sfc_P','sfc_T','sfc_Td','sfc_wdir','sfc_wspd',
    'P910','T910','Td910','900_wdir','900_WS',
    'P850','T850','Td850','850_wdir','850_WS',
    'P700','T700','Td700','700_wdir','700_WS',
    'P500','T500','Td500','500_wdir','500_WS']

    #file = f'{cur_dir}/{station}_sonde{time}z_2000to2020.csv'
    file = f'{station}_sonde{time}z_2000to2020.csv'

    '''  Use picklised one - faster and data is already formatted 
    sonde = pd.read_csv(
        open(os.path.join('app','data',file),'rb'),
        parse_dates=[0],
        index_col=[0],
        names=col_names,
        skiprows=1,
        header=None)
    '''
    sonde = pickle.load(
            open(os.path.join(cur_dir,'app','data',station+'_sonde_'+time+'_aws.pkl'), 'rb'))
    '''
    # for 17 and 23Z use the UTC date of sonde flight as index
    if time:
        if int(time) in [14,15,16,17,18,19,20,21,22,23]:

            sonde.set_index(
                keys=(sonde.index.date),drop=False,inplace=bool(1))
        else: # int(time) == 0:
            sonde.set_index(
                keys=(sonde.index.date - pd.Timedelta(str(1) + ' days')),
                drop=False,inplace=bool(1))
    # we loose datetime type of index in conversion above - restore BLW
    sonde.index = pd.to_datetime(sonde.index)

    file stn066037_2006-7-1.txt
    aifstime[18]="200607011900"  <-- 1900UTC on 1st July
    For FG matching we would be using mostly using either 02, 05, 06, 08 or 11UTC obs
    and sonde from following day (although same UTC day) so when matching we
    get all 0500 UTC obs for station and merge with 1900 or 2300 sonde data - for SAME UTC date
    we could even merge the 05Z METARs with 05Z sonde and use that for synoptic matching as well
    so no problem with fog synop matching.

    For TS matching if we are using 23Z sonde data and 0200Z or 0500Z METARs
    then we need to correct the index for sonde data i.e 2300 UTC sonde date from Nov 1st
    is actually 9am Nov 2nd - the day we need to match for METARs is Nov 2nd and we need to
    change sonde index from Nov 1st to Nov 2nd so that correct sonde data is used for matching.
    We probably need to do same for fog matching if we want to use current days 9am obs together
    with current days 3pm/0500 or 6pm/0800 METARS
    Given this usage depends on context - fog/ or TS matching and whether we want to use observed
    sonde 2300 or 0500 vs forecast 2300Z/0500Z sonde for matching 
    So we leave this reindexing out of the code here.

    file stn066037_2010-11-1.txt
    aifstime[18]="201011010300"  <-- 0300UTC on 1st Nov
    Why do we want to say this data is for 31st Oct by subtracting 1day BELOW?????
    This will stuff up storm day matching at obs wud be from Nov 1st and wrong day sonde!!


    sonde['tmp_rate850_500'] = sonde['T850']-sonde['T500']
    # if only request data at level, return only that level , else return full sonde
    '''
    # this filtering could be easily implemented in client
    if level:
        return sonde[[level+'_wdir', level+'_WS']].astype(float, 'ignore')
    else:
        return sonde

################################################################
'''Extract daily 23Z F160 sonde files for given station
for single day
Uses Hanks extract_skewt_from_adam.pl interface
Downloads daily 2300Z Brisbane sonde as text files '''
###############################################################
def getf160_hanks(station="040842",day='None'):

    # if no date given, retrieve todays sonde data
    if day == 'None':
        day = pd.datetime.today()  #.strftime("%Y-%m-%d")
    else:
       '''our day is in this string format "2018-06-05"
       Need to Convert the string to datetime format, else get
       AttributeError: 'str' object has no attribute 'day' '''
       day = pd.to_datetime(day)   # this also works
       # day = datetime.strptime(day, '%Y-%m-%d')

    print("\n\nGetting f160 sonde from Hanks interface for",day,"\n")


    ''' Convert the other way datetime to string format
        days =  [datetime.strptime(d, '%Y%m%d') for d in dates]
    huge issues with dates formats - Nice tutorial/examples
    see https://www.guru99.com/date-time-and-datetime-classes-in-python.html

    dates = pd.date_range(start=day, end=day, freq='D')
    print("Getting sonde station:{}, day {} or {}".format(station,day,dates[0]))
    print("day:",day,"type",type(day),
          "\npd.to_datetime(day)", type(pd.to_datetime(day)),
          "\nfrom pd.date_range()", type(dates[0]),
          "\ndates",dates)

    '''

    f160_url = 'http://aifs-sa.bom.gov.au/cgi-bin/extract_skewt_from_adam.pl'
    day, month, year = day.day,day.month,day.year
    payload = {'plot':'go', 'd':day,'m':month,'y':year,\
               'stn': station,\
               'prev':'None','exact':'', \
               'ascii':'on','ascii2':'off','reverse':'','crap':9558}

    '''?plot=go&d=1&m=1&y=2010&h=2300&stn=040842&prev=None&exact=&ascii=on&ascii2=off&reverse=&crap=9558'''

    f160_response = requests.get(f160_url, params=payload)

    print (f160_response.url)  #check if url formed correctly

    if (f160_response.status_code == requests.codes.ok):

        print ("Found file resource")
        print (f160_response.headers.get('content-type'),"\n")

        # save response file
        f160_file = cur_dir+'f160/stn'+str(payload['stn'])+'_'+\
        str(year)+'-'+str(month)+'-'+str(day)+'.txt'


        with open(f160_file, 'wb') as f:
            f.write(f160_response.content)

        dat = pd.read_csv(f160_file,skiprows=10, skip_blank_lines=True)

        # drop these 2 cols - have no actual data
        dat.drop(['Geop', 'AbsHum'], axis=1,inplace=True)

        # drop rows with 2 or more NAN/missing
        dat.dropna(axis=0, thresh=2,inplace=True)

        # force convert all data to numeric
        for col in  dat.columns:
            dat[col] = pd.to_numeric(dat[col], errors='coerce')

        # find replace all missing values indicated by -9999 to NaN
        # https://machinelearningmastery.com/handle-missing-data-python/
        dat.replace(-9999,np.NaN, inplace=True)
        #print(dat)

        # drop integer row ids that form inner index
        # n make index datetime index
        # df.index = df.index.droplevel(1)
        # dat.index = pd.DatetimeIndex(day)

        sfc_proxy = dat.iloc[0,:]
        #print(sfc_proxy)

        p_hPa = dat.iloc[:,0]  # get pressure levels as Series

        closest900 = \
            p_hPa[np.abs(p_hPa-900.0) == np.abs(p_hPa-900.0).min()]
        nine100 = dat.iloc[closest900.index.values[0]]

        closest850 = \
            p_hPa[np.abs(p_hPa-850.0) == np.abs(p_hPa-850.0).min()]
        eight50 = dat.iloc[closest850.index.values[0]]

        closest700 = \
            p_hPa[np.abs(p_hPa-700.0) == np.abs(p_hPa-700.0).min()]
        seven100 = dat.iloc[closest700.index.values[0]]

        closest500 = \
            p_hPa[np.abs(p_hPa-500.0) == np.abs(p_hPa-500.0).min()]
        five100 = dat.iloc[closest500.index.values[0]]


        dato = pd.concat(
                [sfc_proxy, nine100,eight50,seven100,five100], axis=0)

        #set index for Series object
        dato.index = ['P','T','Td','wdir','wspd',
                      'P900', 'T900','Td900','wdir900','wspd900',
                      'P850', 'T850','Td850','wdir850','wspd850',
                      'P700', 'T700','Td700','wdir700','wspd700',
                      'P500', 'T500','Td500','wdir500','wspd500']

        dato['tmp_rate850_500'] = dato['T850']-dato['T500']
        print(dato)

    return(dato)



#########################################################
''' For some reason
    http://aifs-sa.bom.gov.au/cgi-bin/extract_skewt_from_adam.pl
    archves has missing data at some of the levels

    However aifs-qld.bom.gov.au has those levels
    This function is to get data from this site although there
    is some difference in number of fields availale

    http://aifs-qld.bom.gov.au/local/qld/rfc/pages/digi.php?id=ybbn&wind=raw
    see aifs-qld-f160-data-format.txt for format '''
##########################################################
def getStation_f160_aifs_qld(station="YBBN"):
    print("\n\nGetting f160 sonde from aifs-qld interface\n")

    day = pd.datetime.today() #.strftime("%Y-%m-%d")
    day, month, year = day.day,day.month,day.year

    f160_url = 'http://aifs-qld.bom.gov.au/local/qld/rfc/pages/digi.php'
    payload = {'id': station, 'wind': 'raw'}

    f160_response = requests.get(f160_url, params=payload)

    print (f160_response.url)  # check if url formed correctly

    if (f160_response.status_code == requests.codes.ok):

        print ("Found file resource")
        print (f160_response.headers.get('content-type'), "\n")

        # save response file
        f160_file = \
            '/tmp/f160/stn' + str(payload['id']) + '_' + \
            str(year) + '-' + str(month) + '-' + str(day) + '.txt'

        with open(f160_file, 'wb') as f:
            f.write(f160_response.content)

        dat = pd.read_csv(f160_file, skiprows=10, skip_blank_lines=True)

        # drop rows with 2 or more NAN/missing
        dat.dropna(axis=0, thresh=2, inplace=True)

        # force convert all data to numeric
        for col in dat.columns:
            dat[col] = pd.to_numeric(dat[col], errors='coerce')

            # find replace all missing values indicated by -9999 to NaN
        # https://machinelearningmastery.com/handle-missing-data-python/
        dat.replace(-9999, np.NaN, inplace=True)
        print(dat)

        # drop integer row ids that form inner index
        # n make index datetime index
        # df.index = df.index.droplevel(1)
        # dat.index = pd.DatetimeIndex(day)

        sfc_proxy = dat.iloc[0, :]
        print(sfc_proxy)

        # five100_proxy = dat.apply(closest_to_500)
        p_hPa = dat.iloc[:, 0]
        print(p_hPa)

        closest500 = \
            p_hPa[np.abs(p_hPa - 500.0) == np.abs(p_hPa - 500.0).min()]
        print(closest500)
        print(closest500.index.values[0])

        five100_proxy = dat.iloc[closest500.index.values[0]]
        print(five100_proxy)

        dato = pd.concat([sfc_proxy, five100_proxy], axis=0)
        # set index for Series object
        dato.index = ['P', 'Z', 'wdir', 'wspd', 'P500', 'T500', 'Td500', 'wdir500', 'wspd500']
        # print(dato)

    return (dato)



####################################################################
'''
Get f160 data files using sql query direct from adamprd
[vinorda@qld-rfc-ws38 ~]$ sqlplus anonymous/anonymous@adamprd
SQL*Plus: Release 11.2.0.1.0 Production on Wed May 16 19:01:52 2018
Copyright (c) 1982, 2009, Oracle.  All rights reserved.
Connected to:
Oracle Database 11g Enterprise Edition Release 11.2.0.4.0 - 64bit Production
With the Partitioning, Real Application Clusters, Automatic Storage Management, OLAP,
Data Mining and Real Application Testing options

SQL> desc uas
 Name                                      Null?    Type
 ----------------------------------------- -------- ----------------------------
 STN_NUM                                   NOT NULL NUMBER(6)
 TM                                        NOT NULL DATE
 PRES                                      NOT NULL NUMBER(7,1)
 PRES_QUAL                                          NUMBER(2)
 LEVEL_TYPE                                         NUMBER(1)
 GEOP_HT                                            NUMBER(8,1)
 GEOP_HT_QUAL                                       NUMBER(2)
 AIR_TEMP                                           NUMBER(7,1)
 AIR_TEMP_QUAL                                      NUMBER(2)
 DWPT                                               NUMBER(7,1)
 DWPT_QUAL                                          NUMBER(2)
 WND_DIR                                            NUMBER(5,1)
 WND_DIR_QUAL                                       NUMBER(2)
 WND_SPD                                            NUMBER(5,1)
 WND_SPD_QUAL                                       NUMBER(2)
 OB_QUAL_FLAG                                       NUMBER(2)
 MSG_ID                                             NUMBER(38)
 CMT                                                VARCHAR2(240)

"tm" is in UTC.

Message from Hank
Until they either fix the TTAA messages or change the decoder to accept them
the standard levels won't get into ADAM.

The upper temp messages (TTAA/BB/etc) are all archived to the one structure in ADAM,
which is the one I query for the SkewT plotting web page.

My SQL queries are:


    $query =
      " select tm,pres,air_temp,dwpt,geop_ht from uas where stn_num=$stn
        and tm between '$start_date' and '$end_date'
        and air_temp is not null
        and pres>=100
        order by tm,-1*pres;
        select tm,pres,wnd_dir,wnd_spd*2 from uas where stn_num=$stn
        and tm between '$start_date' and '$end_date'
        and wnd_dir is not null
        and pres>=$min_pressure
        order by tm,-1*pres;
      ";

'''
##########################################################################
# Requires import cx_Oracle
#          from pandas.io import sql
# for batch process/download specify both start and end dates
# and comment return statement and uncomment 2 lines above return

def getf160_adams(station_number=40842, start_date='None',end_date='None'):

    print("\n\nGetting f160 sonde from ADAMS interface\n")

    conn = cx_Oracle.connect(user='anonymous', password='anonymous', dsn='adamprd')
    # cursor = conn.cursor()
    hr = datetime.utcnow().hour # pd.datetime.today().hour

    '''Note: seems we can't get current days sonde data from ADAMS
       not until a few hours after sonde launch
       Quality assurance issues maybe - so set back one day and get
       yesterdays sonde
       Other option is use Bretts interface on aifs-qld
       http://aifs-qld.bom.gov.au/local/qld/rfc/pages/digi.php '''
    '''
    if (start_date is 'None'): # | (end_date is 'None'):
        if ((hr > 14) & (hr < 24)):
            # we have to set start date one day since its new calendar day!!
            start_date = (pd.datetime.today() - pd.Timedelta('1 days'))\
                        .strftime("%Y-%m-%d")
            end_date = (pd.datetime.today() + pd.Timedelta('1 days')) \
                .strftime("%Y-%m-%d")

            query = (
                "SELECT stn_num,tm,pres,geop_ht,air_temp,dwpt,wnd_dir,round(wnd_spd*1.943) as wnd_spd FROM UAS "
                "WHERE STN_NUM={station_number} "
                "AND TM between TO_DATE('{start_date}', 'yyyy-mm-dd') "
                "AND TO_DATE('{end_date}', 'yyyy-mm-dd') "
                "AND TO_CHAR(tm,'hh24') in (16,17,18,19,20,21,22,23) "
                "ORDER by tm,-1*pres"
            ).format(
                start_date=start_date, end_date=end_date, station_number=station_number
            )
        else:
            # Note we increment end_date by 1 day to provide a range
            start_date = (pd.datetime.today() - pd.Timedelta('1 days'))\
                        .strftime("%Y-%m-%d")
            end_date = (pd.datetime.today() + pd.Timedelta('1 days'))\
                        .strftime("%Y-%m-%d")
            query = (
                "SELECT stn_num,tm,pres,geop_ht,air_temp,dwpt,wnd_dir,round(wnd_spd*1.943) as wnd_spd FROM UAS "
                "WHERE STN_NUM={station_number} "
                "AND TM between TO_DATE('{start_date}', 'yyyy-mm-dd') "
                "AND TO_DATE('{end_date}', 'yyyy-mm-dd') "
                "AND TO_CHAR(tm,'hh24') in (00,01,02,03,04,05,06) "
                "ORDER by tm,-1*pres"
            ).format(
                start_date=start_date, end_date=end_date, station_number=station_number
            )
    '''
    if (start_date is 'None'): # | (end_date is 'None'):
        # we have to set start date one day back due 23Z time issues
        start_date = (pd.datetime.today() - pd.Timedelta('1 days'))\
                        .strftime("%Y-%m-%d")
        end_date = pd.datetime.today().strftime("%Y-%m-%d")

    #start_date = pd.to_datetime(start_date)

    print(start_date,end_date)

    # Note in the SQL we increment end_date by 1 day
    query = (
    "SELECT stn_num,tm,pres,geop_ht,air_temp,dwpt,wnd_dir,round(wnd_spd*1.943) as wnd_spd FROM UAS "
    "WHERE STN_NUM={station_number}"
    "AND TM between TO_DATE('{start_date}', 'yyyy-mm-dd')"
    "AND TO_DATE('{end_date}', 'yyyy-mm-dd') + 1 "
    "AND TO_CHAR(tm,'hh24') in (22,23,00,01,02,03)"
    # "AND TO_CHAR(tm,'hh24') = '23' " <-- Don't
    # "AND pres IN (910,850,700,500)"
    # "AND pres is NOT NULL"   ERROR OR-00908 mising null keyword
    "ORDER by tm,-1*pres"
    ).format(
    start_date=start_date, end_date=end_date, station_number=station_number
    )

    print(query)
    print(f"\nCurrent hour = {hr}. Sonde data from {start_date} to {end_date}")

    return(sql.read_sql(query, conn, parse_dates=['TM'], index_col='TM'))


#############################################################
'''Process data downloaded in batch mode using above fn
   getf160_adams(station_number=40842,
                start_date='2000-01-01',end_date='2018-05-24')


   data file was saved as cur_dir/'f160/sonde_data_adam_2000to2018.csv'

   USAGE fom main()

  sonde_data_adams = pd.read_csv(cur_dir+'f160/sonde_data_adam_2000to2018.csv',
      parse_dates=[0], index_col=0)

  for col in  sonde_data_adams.columns[1:]:
    sonde_data_adams[col] = pd.to_numeric(sonde_data_adams[col], errors='coerce')

  sonde_data_final = sonde_data_adams.resample('D').apply(bous.process_adams_f160)

  sonde_data_final['LTM']= pd.to_datetime(sonde_data_final['LTM'])
  # if hour is 22 or 23 increment date by 1, if 00Z no date change
  sonde_data_final['dates'] = [ (x+pd.Timedelta('1 days')).date() \
  if ((x.hour == 22)|(x.hour == 23)) else x.date() \
  for x in sonde_data_final['LTM']]

  sonde_data_final['dates'] = pd.to_datetime(sonde_data_final['dates'])
  sonde_data_final.set_index('dates', inplace=True)
'''

def get_std_levels_adams(x):
    fields = ['STN_NUM', 'P', 'Z', 'T', 'Td', 'wdir', 'wspd',
              'STN_NUM', 'P900', 'Z900', 'T900', 'Td900', 'wdir900', 'wspd900',
              'STN_NUM', 'P850', 'Z850', 'T850', 'Td850', 'wdir850', 'wspd850',
              'STN_NUM', 'P500', 'Z500', 'T500', 'Td500', 'wdir500', 'wspd500',
              'tmp_rate850_500', 'gpt_rate', 'lr850_500', 'LTM']

    # if no data for this date
    if x.empty:
        # print("No sonde data for this day - not even have date!", x.index.time[:1])
        return (pd.Series(index=fields, data=np.nan))

    #21# x['WND_SPD'] = round(1.942 * x['WND_SPD'], 1)

    try:
        p_hpa = x.iloc[:, 1]  # Series pressure values in 2nd col, 1st col STN_NUM
    except:
        print("Something went wrong this day, no pressure values - DISCARD", x.index[:1])
        # print(p_hpa)
        # return (pd.Series(index=fields, data=np.nan))
        # print(p_hpa)

    # fix  winds - convert to knots - round to 1 dp
    # we do this on whole dataset before calling this function
    # x['WND_SPD'] = round(1.942 * x['WND_SPD'], 1)

    '''
    Most of the time this will work
    lv850 = x.loc[x['PRES'] == 850].iloc[0]  # a series of 850 params
    lv500 = x.loc[x['PRES'] == 500].iloc[0]  #
    but if we have missing standard levels need to find level closest'''

    lv900 = x.loc[ \
        np.abs(p_hpa - 900.0) == np.abs(p_hpa - 900.0).min()].iloc[0] \
        .squeeze()


    lv850 = x.loc[ \
        np.abs(p_hpa - 850.0) == np.abs(p_hpa - 850.0).min()].iloc[0] \
        .squeeze()
    '''need .iloc[0] as sometimes more than 1 row may match '''

    lv500 = x.loc[ \
        np.abs(p_hpa - 500.0) == np.abs(p_hpa - 500.0).min()].iloc[0] \
        .squeeze()

    '''
    # if no data at 850, 500 or levels closest return NaNs 4 this day
    p_850 = lv850['PRES']
    p_500 = lv500['PRES']

    if (~(p_850 == 850)) | (~(p_500 == 500)):
        print("Missing standard levels for this day", x.index[:1])
        print("So we used these closest levels instead")
        print ("p_850", p_850, "p_500", p_500)
    '''
    # many ways to check if any field is missing in std level
    # lv850[lv850.isin([np.nan])].empty
    # lv850.index[lv850==""]  # if missing value is just a blank

    # lv850.index[lv850.isnull()] gives indices list for missing values
    # if len list non zero - we have missing data

    # SOME SETS REMARKED SO AS NOT TO THOW AWAY DATA WE DO HAVE
    # each level has 7 data values including STN_NUM
    # if 5 or more values for level missing than we discard day
    if np.logical_and(
                    lv850.isnull().sum() > 5,
                    lv500.isnull().sum() > 5):
        print("Had 5 or more missing values at 850 and 500-DISCARD", x.index[:1])
        return (pd.Series(index=fields, data=np.nan))

    '''
    if (len(lv850.index[lv850.isnull()]) > 5) &\
       (len(lv500.index[lv500.isnull()]) > 5):
        print("we had missing values")
        return(pd.Series(index=fields, data=np.nan))


    # since we only care about missing 'AIR_TEMP' and 'GEOP_HT'
    if ( lv850.index[lv850.isnull()].isin(['AIR_TEMP','GEOP_HT'])) |
       ( lv500.index[lv500.isnull()].isin(['AIR_TEMP','GEOP_HT'])):
        print("we had missing values")
        return(pd.Series(index=fields, data=np.nan))
    '''

    '''
    if  x.loc[x['PRES'] == p_850].empty :
        print("Missing 850 data for this day",x.index[:1])
        return(pd.Series(index=fields, data=np.nan))
    if  x.loc[x['PRES'] == p_500].empty :
        print("Missing 500 data for this day",x.index[:1])
        return(pd.Series(index=fields, data=np.nan))
    '''

    # grab sfc values - lowest sonde level shud be 1st record
    lvsfc = x.iloc[0, :]

    dat = pd.concat([lvsfc, lv900, lv850, lv500], axis=0)

    tmp_rate = lv850['AIR_TEMP'] - lv500['AIR_TEMP']
    gpt_rate = lv500['GEOP_HT'] - lv850['GEOP_HT']
    dat['tmp_rate850_500'] = tmp_rate
    dat['gpt_rate'] = gpt_rate
    dat['lr850_500'] = round(dat['tmp_rate850_500'] / dat['gpt_rate'] * 1000, 1)

    # for date use datetime for 1st sonde record for this day
    dat['LTM'] = pd.to_datetime(x.index, format='%Y-%m-%d %H:%M:S', errors='coerce')[0]
    dat['LTM'] = pd.to_datetime(x.index, infer_datetime_format=True)[0]

    dat.index = fields

    return (dat)



################################################################
'''Sonde data downloaded using direct SQL query to ADAM has
   datetime with 22Z or 23Z
   Such dates should be incremented to next/following calendar day
   When batch processing sonde using .resample('D')
   sonde_data_final =  sonde_data_adams.resample('D')\
                    .apply(bous.process_adams_f160)

   resample('D') only uses the date portion as index
   truncates/ignores the time bit 22Z/23Z etc
   Here we use the saved time info to save record with
   next days timestamp if time was like 22Z or 23Z
'''
################################################################

def process_adams_sonde(dat):

    # 1st modify 'LTM' the field with both date and time
    # to be datetime aware/datetime like!!
    dat['LTM']  = pd.to_datetime(dat['LTM'])

    # if hour is 22 or 23 increment date by 1 else no change
    dat['dates'] = [ (x+pd.Timedelta('1 days')).date() \
     if ((x.hour == 22)|(x.hour == 23)) else x.date() \
     for x in dat['LTM']]

    # dats not datetime like - force it
    dat['dates'] = pd.to_datetime(dat['dates'])
    # now set as index
    dat.set_index('dates', inplace=True)
    # this wud by default drop curent index 'TM'
    # drop 'STN_NUM' from columns
    dat.drop(labels=['STN_NUM'], axis=1, inplace=True)
    # Drop records/rows where ALL cell values in that row is missing NaN
    dat.dropna(how='all', inplace=True)


    '''add calendar day to serve as numeric equivalent of month-day combination'''
    dat['day'] = dat.index.dayofyear

    '''To trully be able to capture seasonal variations
    we have to convert calendar day to a categorical variable.
    We can bin months like this '''
    # DJF 'summer',MAM  'autumn', JJA 'winter', SON 'spring'
    seasons = {'summer': [12, 1, 2], 'autumn': [3, 4, 5],
               'winter': [6, 7, 8], 'spring': [9, 10, 11]}

    dat['season'] = ''
    for k, v in enumerate(seasons):
        # print (v,seasons[v])
        # print(obs.index.month.isin(seasons[v]))
        dat.loc[dat.index.month.isin(seasons[v]), 'season'] = v

    ''' dat['TS'] = .... We don't know it tis daate had storms yet!!! '''

    '''Best solution so far when deciding which record to remove
    for records with same date; remove rowwith  more missing data'''

    dat = dat.reset_index()
    # this is very clever!!!
    dat = dat.loc[dat.notnull().sum(axis=1).groupby(dat['dates']).idxmax()]
    # now put dates back as index
    dat = dat.set_index(['dates'])

    return(dat)


############################################################
## Functions for basic time and timedelta conversions
## TS stats start,end times and duration
## conversion to decimal representation for ease of plotting
## plotting routines etc
#############################################################

## Convert time HH:MM format to decimal HH.mm
'''60 minutes make an hour -  each minute is one-sixtieth (1/60) of an hour.
   Basis for converting number of minutes into fractions of an hour.
   To this for ease of plotting time as floats on y-axis
   1/60 = 0.016666666666666666
'''
def conversion(x):
    h,m,s = x.split(':')
    return (int(h) + int(m)/60 + int(m)/60/60)


'''
Helper function to convert timedelta object
to 'HH:MM:SS' format (DON'T REALLY Need them!!)
'''
def convert_timedelta(duration):
    #days, seconds = duration.days, duration.seconds
    seconds=duration.seconds
    hrs =   seconds // 3600
    mins = (seconds % 3600) // 60
    secs = (seconds % 60)
    ret = '{}:{}:{}'.format(hrs,mins,secs)
    # ret = '%s:%s:%s' % (hrs,mins,secs)
    return (ret)

'''
function takes in the duration string "%H:%M:%S" format
and uses datetime.strptime(date_string,format)

Return a datetime corresponding to date_string,parsed according to format.
assert(t.hour*60*60+t.minute*60+t.second == delta.total_seconds())
'''

def duration_to_timedelta(dt):
    t = datetime.strptime(dt,"%H:%M:%S")
    delta = timedelta(hours=t.hour,minutes=t.minute,seconds=t.second)
    return (delta)

'''
Two datetime64 cols ('first','last')
first       703 non-null datetime64[ns]
last        703 non-null datetime64[ns]
duration    703 non-null timedelta64[ns]

'duration' col is timedelta64

UTC        first                last                duration
1985-01-06 1985-01-06 06:35:00  1985-01-06 12:30:00 05:55:00

To plot PDF's of these we need continous numeric so need to convert these to floats
(actually not really need to do this)

Here we first have to strip the date out from the datetime64 cols
('first' and 'last')
then convert the remaining time data to decimal representation - unnecessary...
'''

def format_datetimes(df):

    dataf = df.copy() # we don't want to modify passed df

    # dataf[['first','last']].apply(lambda x: datetime.strftime(x,'%H:%M:%S')).apply(conversion)
    # TypeError: ("descriptor 'strftime' requires a 'datetime.date' object but received a 'Series'", 'occurred at index first')

    '''applying for each series in turn works though'''
    dataf['first']= dataf['first']\
        .apply(lambda x: datetime.strftime(x,'%H:%M:%S'))\
        .apply(conversion)
    dataf['last'] = dataf['last']\
        .apply(lambda x: datetime.strftime(x,'%H:%M:%S'))\
        .apply(conversion)

    # Convert hh:mm:ss to minutes
    # daily['duration'] = daily['duration'].apply(lambda x :duration_to_timedelta(str(x)))
    '''
    fixed in get_ts_start_end_duration(dat)
    duration = pd.DatetimeIndex(dataf['duration'])
    dataf['duration'] = \
    (duration.hour*60*60 + duration.minute*60 + duration.second)/(60*60.0)
    '''
    # dataf['duration'] = dataf['duration'].apply(conversion)
    '''AttributeError: 'Timedelta' object has no attribute 'split'''

    # dataf['duration'] = dataf['duration'].apply(lambda x: datetime.strftime(x,'%H:%M:%S')).apply(conversion)
    '''TypeError: descriptor 'strftime' requires a 'datetime.date' object but received a "Timedelta"'''

    return(dataf)



#### Function to plot TS start/end/duration stats
#### Same function used for aws obs and gpats data

def plot_ts_stats(ts_df):

    #import matplotlib.pyplot as plt
    #import seaborn as sns
    import format_datetimes

    # convert datetime/deltatime to equivalent float representation
    dat = format_datetimes(ts_df)
    # dat = ts_df.copy()

    (fig, axes) = plt.subplots(figsize=(14,18) , nrows=4, ncols=1 )

    # get num of ts days by month for bar chart
    ts_days_by_month = \
        dat.groupby(dat.index.month).size()


    ts_days_by_month.plot( kind='bar', ax=axes[0])
    axes[0].set_title("Total Num of Thunderstorm Days per month", color='b',fontsize=15)
    axes[0].set_ylabel('Num of Thunder Days', color='g', fontsize=20)
    axes[0].tick_params(labelsize=10)

    # box plots for median and pdf of onset/end/duration
    sb.boxplot(data=dat, x=dat.index.month, y="first", linewidth=2, ax=axes[1])
    axes[1].set_title("Thunderstorm Onset", color='b',fontsize=15)
    axes[1].set_ylabel('TS Onset Time (UTC)', color='g', fontsize=20)
    axes[1].tick_params(labelsize=10)

    sb.boxplot(data=dat, x=dat.index.month, y="last", linewidth=2, ax=axes[2])
    axes[2].set_title("Thunderstorm Finish", color='b',fontsize=15)
    axes[2].set_ylabel('TS End Time (UTC)', color='g', fontsize=20)
    axes[2].tick_params(labelsize=10)

    sb.boxplot(data=dat, x=dat.index.month, y="duration", linewidth=2, ax=axes[3])
    axes[3].set_title("Thunderstorm Duration Hours", color='b',fontsize=15)
    axes[3].set_ylabel('TS Duration (hours)', color='g', fontsize=20)
    axes[3].set_xlabel('MONTHS OF THE YEAR', color='r', fontsize=15)
    axes[3].tick_params(labelsize=10)




### No longer require tis #############
def gpats_format_datetimes(gpats):

    gpats_ts_stats = gpats.copy()

    duration=gpats_ts_stats['duration'].apply(lambda x:convert_timedelta(x) )
    # get back datetime from duration string - no more micro-sec!!!
    duration = duration.apply(lambda x: datetime.strptime(x, "%H:%M:%S"))
    # nb duration ow longer timedelta but shud not matter

    # datetime to string so we can strip microseconds
    first = gpats_ts_stats['first'].dt.strftime("%Y/%m/%d %H:%M:%S")
    # get back datetime from new datetime string - no more micro-sec!!!
    first = first.apply(lambda x: datetime.strptime(x, "%Y/%m/%d %H:%M:%S"))

    last = gpats_ts_stats['last'].dt.strftime("%Y/%m/%d %H:%M:%S")
    last = last.apply(lambda x: datetime.strptime(x, "%Y/%m/%d %H:%M:%S"))

    gpats_ts_stats['duration'] = duration
    gpats_ts_stats['first'] = first
    gpats_ts_stats['last'] = last

    return(gpats_ts_stats)




############################################################
#### TS DATES / STATS FROM ORIG MSG COL ####################
'''
orig_msg_only = df.iloc[:,[0,54]].copy()

# Find and replace/delete trend/TTF part from all raw messages
no_trend = orig_msg_only['MSG'].str.\
    replace(r'TTF|FM\d{4}|TEMPO|INTER.*', '', case=False)

# add as new series to df
# no_trend field is original message text stripped of TTF
orig_msg_only.loc[:,'no_trend'] = no_trend

orig_msg_only['no_trend_RMK'] = \
    orig_msg_only['no_trend'].str.cat(df['RMK'])

msg_ts_mask = orig_msg_only['no_trend_RMK'].str.\
              contains(r'[vc|re|ra|+|-]?TS\w*|Thunder|Lightning',case=False)

msg_ts_mask.fillna(False, limit=1,inplace=True)

#---------------------------------------------------
#  save mask for later use
import  pickle
with open('~/data/msg_ts_mask.pkl', 'wb') as f:
    pickle.dump(msg_ts_mask, f)

msg_ts_stats = get_ts_start_end_duration(\
						df.loc[msg_ts_mask].copy())
# Filter zero duration TS events
msg_ts_stats = \
        msg_ts_stats[msg_ts_stats['duration'] > 0]

ts_dates_from_msg = msg_ts_stats.index

'''
#########################################################
###### MERGE AWS DATA WITH NETCDF DATA ##################
'''
df_final = df.merge(
    sta_df500_about_YBBN,
    how='left',
    left_index=True, right_index=True)

with open('~/data/obs_ec_reanal_merge.pkl', 'wb') as f:
    pickle.dump(df_final[keep], f)


with open('~/data/obs_ec_reanal_merge.pkl', 'wb') as f:
    df_final = pickle.load(f)
'''

'''Most netcdf data are 3D [TIME,X,Y]
e.g times slices of a variable for a given lat/lon box
'''

def get_dimensions(nc_data):

    import netCDF4 as nc    # netcdf module

    print ('Dimensions of nc data file')
    dim_keys = nc_data.dimensions.keys()
    print(dim_keys)

    print('Read latitide and longitude')
    x = nc_data.variables['longitude'][:] # read longitude variable
    y = nc_data.variables['latitude'][:] # read latitutde variable

    print("Longitude:len=",len(x),x)
    print("Latitude: len=",len(y),y)

    print('Read time and do conversion')
    # read the 'units' attributes from the variable time
    time_unit = nc_data.variables["time"].getncattr('units')
    print(time_unit)
    # 'calendar' type attributes from the variable time
    time_cal = nc_data.variables["time"].getncattr('calendar')
    print(time_cal)
    # convert time
    time = nc_data.variables['time'][:]
    print("Time:len=",len(time))
    local_time = nc.num2date(nc_data.variables['time'][:],units=time_unit, calendar=time_cal)

    print("First data point time %s ->\t\t: %s"
      % (time[0], local_time[0])) # check conversion
    print("Last  data point time %s ->\t: %s"
      % (time[-1], local_time[-1])) # check conversion

    '''Data usually 3D [TIME, LONG (X), LAT (Y)]
    Some netcdf have extra 4th dimension, multiple pressure levels'''
    if ('level' in list(dim_keys)):
        levels = nc_data.variables['level'][:] # read longitude variable
        print("Pressure Levels: len=",len(levels),levels)
        return (local_time,levels,x,y)
    else:
        return (local_time,x,y)



# read airport lat long coordinates from given AV_ID
# from avlocs database
def get_sta_latlon(sta):

    # avlocs_url = 'http://web.bom.gov.au/cosb/dms/mgdu/avloc/avloc.csv'
    avlocs_url = '~/data/avloc.csv'
    avlocs = pd.read_csv(avlocs_url, header=0, sep=';', comment='#',index_col='av_id')
    # sta_name = 'Gold coast'
    # name_mask = avlocs['name'].str.contains(sta_name.upper(), case=False)
    # Lots of locations with same name - useless!

    sta = sta.upper()
    lat_lon = avlocs[avlocs['type'] == 'AD'].loc[sta][['latitude','longitude']].values
    return lat_lon


'''
Find closest grid point to station.
This grid point is then used to extract
relevant variables for this location from netcdf file

ECMWF have a Python interface to ecCodes that does this
for us. Not sure they have one for netcdf.
http://download.ecmwf.int/test-data/eccodes/html/namespaceec_codes.html
https://software.ecmwf.int/wiki/display/ECC/grib_nearest
codes_grib_find_nearest() '''

'''
Parameters
sta_id : station aviation id like YBBN or YTWB
nc_id  : netcdf data file handle
grid_size: grid spacing in degrees, 0.25, 0.5 etc

Return
(x_index, y_index): the integer indices
corresponding to grid point location closest to station
'''

def nearest_grid_point(sta_id,nc_id,grid_size=0.5):

    # To create lat/lon grids manually
    # latitude = np.arange(lat_min, lat_max, grid_size)
    # longitude = np.arange(lon_min, lon_max, grid_size)

    latitude = nc_id.variables['latitude'][:]
    longitude = nc_id.variables['longitude'][:]
    lat_min=np.min(latitude)
    lat_max=np.max(latitude)
    lon_min=np.min(longitude)
    lon_max=np.max(longitude)

    print ("min lat:%s\tmax lat:%s\tmin long:%s\tmax long:%s" %(lat_min,lat_max, lon_min,lon_max))

    (stn_lat, stn_lon) = get_sta_latlon(sta_id)

    '''Create 2D array mesh grid of our area
    for which we had extracted model data'''

    # Use meshgrid to make 2D arrays of the lat/lon data above
    lats, lons = np.meshgrid(latitude, longitude)

    '''
    Now find the absolute value of the difference between
    the  station's lat/lon with every point in the grid.
    This tells us how close a point is to the particular
    latitude and longitude.'''

    abslat = np.abs(lats-stn_lat)
    abslon = np.abs(lons-stn_lon)

    '''
    Now we need to combine these two results.
    We will use numpy.maximum,
    which takes two arrays and finds the local maximum.'''

    c = np.maximum(abslon, abslat)

    '''find the index location on the grid of this
    by using the min function.'''

    latlon_idx = np.argmin(c)

    '''Now, this latitude/longitude index value is the index
    for a flattened array, so when you look for that same index value in,
    say, your temperature array,
    you should flatten the array to pluck out the value at that point.
    '''
    # grid_temp = data.flat[latlon_idx]
    '''
    If you don't like flattened arrays,
    you can also get the row/column index like this '''
    x, y = np.where(c == np.min(c))
    #grid_data = data[x[0], y[0]]
    grid_lat = lats[x[0], y[0]]
    grid_lon = lons[x[0], y[0]]

    print ("Station %s coordinates are %s,%s\
    \nNearest grid point location is %s,%s" \
       %(sta_id,stn_lat,stn_lon,grid_lat, grid_lon ))

    # get longitude x-index and lat y-index
    x_index = int(np.abs(grid_lon - lon_min)/grid_size)
    y_index = int(np.abs(grid_lat - lat_min)/grid_size)


    return (x_index, y_index)


'''
Note http://james.hiebert.name/blog/work/2015/04/18/NetCDF-Scale-Factors/

Packing floating point numbers into smaller data types
has the potential to half or quarter the data input or
output requirements for an application.

To scale grid date before writing to netcdf format - need to apply
correct scale factor and offset

packing/unpacking function requires three parameters:
the max and min of the data, and n, the number of bits
into which you wish to pack (8 or 16)

SEE ALSO
https://www.unidata.ucar.edu/software/netcdf/workshops/2010/bestpractices/Packing.html
'''

def compute_scale_and_offset(min, max, n):
    # stretch/compress data to the available packed range
    scale_factor = (max - min) / (2 ** n - 1)
    # translate the range to be symmetric about zero
    add_offset = min + 2 ** (n - 1) * scale_factor
    return (scale_factor, add_offset)


# simple packing and unpacking function:

def pack_value(unpacked_value, scale_factor, add_offset):
    return np.floor((unpacked_value - add_offset) / scale_factor)

def unpack_value(packed_value, scale_factor, add_offset):
    return packed_value * scale_factor + add_offset

## get wind direction given U and V vectors
## courtesy G.Buis
def get_wind_dir(u,v):
    rad2deg = 57.2957795
    temp = 270.0 - (rad2deg * np.arctan2(v, u))
    wdir = [(d-360) if (d>=360) else d for d in temp]
    return(wdir)

## get wind speed given U and V vectors
def get_wind_spd(u,v):
    return(np.sqrt(u**2 + v**2))

'''
https://software.ecmwf.int/wiki/display/CKB/ERA-Interim%3A+compute+geopotential+on+model+levels
'''
# Geopotential z:units = "m**2 s**-2"
# divide geopotential by the gravity of Earth
# (9.80665 m s**-2 about 9.8 m



##################################################################
'''Get list of months spanning the time period for which
   analogues are sought
   https://stackoverflow.com/questions/34898525/generate-list-of-months-between-interval-in-python/34899127
'''
def get_month_list(my_date,period):

    '''VERY SILLY HACK TO GET MONTHS IN DATA WINDOW
    we want to look at all aws data for months between
    start month and end month inclusive
    For e..g if start mon is 11 and end month is 3
    we want all month in between so [11,12,1,2,3] i.e.
    grab data for 5 month period centered on January '''

    start = pd.to_datetime(my_date) - pd.Timedelta(str(period)+' days')
    end =   pd.to_datetime(my_date) + pd.Timedelta(str(period) + ' days')

    daterange = pd.date_range(start=start, end=end,freq='1M')
    daterange = daterange.union([daterange[-1] + 1])
    return([int(d.strftime('%m')) for d in daterange])


'''
#####################################################
FUNCTION to grab data for a time period centered
on the day for which TS forecast is sought.

Look for historical analogues for period 6 weeks wide period
spanning 21 days (3 weeks) either side of date specified
or today() if no date parameter passed

Ideally we would like to filter by calendar days
but for time being we grab data for current month
plus 1 month either side of curr month
########################################################
'''

# http://cryptroix.com/2016/10/09/hello/
# http://blog.thedigitalcatonline.com/blog/2015/02/11/default-arguments-in-python/
'''we can use both standard and default arguments in a function,
but the order in which they appear in the function prototype is fixed:
all standard arguments first, then the default ones OK
'''

# Dates = namedtuple('Dates', ('cur_day', 'period', 'start', 'end'))
def grab_data_period_centered_day_aws(df_final,period=21, day=None):

    print('Processing {}: Data grab window is {} X 2 (days) wide'.format(day,period))

    '''
    month_map = pd.Series(
    index=list(range(1,13)),\
    data=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    '''
    # get dates for start/end of 6 week period centered on given date
    if (day):
        cur_mon = day.month
        start = pd.to_datetime(day) - pd.Timedelta(str(period)+ ' days')
        end =   pd.to_datetime(day) + pd.Timedelta(str(period)+ ' days')
    elif (day is None):
        # no date supplied, build period centered on today()
        cur_mon = int(pd.datetime.today().strftime("%m"))
        # print("Day is None, Use Current Month", cur_mon)
        start = pd.datetime.today() - pd.Timedelta(str(period)+ ' days')
        end = pd.datetime.today() + pd.Timedelta(str(period)+ ' days')
    else:
        print("This can never happen - ever !!!")

    '''
    # df_final_Jan = df_final.loc[df_final.index.month==cur_mon, keep]

    num_days = len(pd.date_range(start,end))

    start_mon,start_day = int(start.strftime("%m")),int(start.strftime("%d"))
    end_mon,end_day =   int(end.strftime("%m")),int(start.strftime("%d"))
    '''
    month_list = get_month_list(day,period)

    print ("start = {}, end = {}".format(start,end))
    print ("Analogue months wud be {}".format(month_list))
    '''
    print ("Looking for analogues through months between {} {} and {} {}\
    centered on {}"\
           .format(month_map.loc[start_mon], start_day,\
                  month_map.loc[end_mon], end_day,\
                  day.strftime("%Y:%m:%d"))) # pd.datetime.today().strftime("%Y:%m:%d")))
    '''
    return (df_final\
            .loc[df_final.index.month.isin(month_list)]\
            .between_time(start_time='00:00',
                end_time='00:05',include_start=True,
                include_end=False)\
            .resample('H').first().dropna(how='all'))


'''
########################################################
FUNCTION to build envelopes for synoptic parameters T,Td,etc
then create a mask using the envelope to extract matching
days from data set.
Returns num of matching days found and how many of those
matching days actually had TS
#########################################################
'''
# Params = namedtuple('Params', ('uwdir1', 'uwdir2', 'uwspd1', 'uwspd1'))
# https://jeffknupp.com/blog/2012/11/13/is-python-callbyvalue-or-callbyreference-neither/

cols_display = ['any_ts','T','Td','QNH','WS', 'WDir', 'MaxGust10min','vis',
       'vis_min_dir', 'vis_aws', 'PW', 'PW1_desc', 'PW2_desc', 'WDIR_DLM','WSPD_DLM','T500','date']

def calculate_percent_chance_ts_aws(df_period, obs_4day):

    print("Obs for day", obs_4day)

    # 60 deg upper 500 wind dir window
    UDL = obs_4day['wdir_500']-30
    UDR = obs_4day['wdir_500']+30

    steering_dir_mask = \
                (df_period['WDIR_DLM'] >= UDL) & \
                (df_period['WDIR_DLM'] <= UDR)


    # TWO  special cases
    # Cases r exclusive - only one can happen at a time

    # CASE 1: UDL NEGATIVE WHEN obs_4day['wdir_500'] < 30
    # a negative wind direction
    # e.g. if wdir=10 ---> UDL=10-30=-20
    if (UDL < 0):
        print("500 dir = ", obs_4day['wdir_500'])
        UDL = 360 - abs(UDL)
        print("New UDL: {} UDR: {}".format(UDL,UDR))
        steering_dir_mask = \
        (df_period['WDIR_DLM'] >= UDL) | \
        (df_period['WDIR_DLM'] <= UDR)

    # CASE 2: UDR GTR THAN 360 if obs_4day['wdir_500'] > 330
    # will give a wind direction > 360
    # say if wdir=350  ---> UDR=350+30=380
    if (UDR > 360):
        print("500 dir = ", obs_4day['wdir_500'])
        UDR = 30 - (360 - obs_4day['wdir_500'])
        print("New UDL: {} UDR: {}".format(UDL,UDR))
        steering_dir_mask = \
        (df_period['WDIR_DLM'] >= UDL) | \
        (df_period['WDIR_DLM'] <= UDR)

    #print("UDL: {} UDR: {} USL: {} USR: {} UTL: {} UTR: {} SPL: {} SPR: {} STdL: {} STdR: {} "\
    #      .format(UDL,UDR,USL,USR,UTL,UTR,SPL,SPR,STdL, STdR))

    USL = obs_4day['wspd_500']-10
    USR = obs_4day['wspd_500']+10
    steering_spd_mask = (df_period['WSPD_DLM'] > USL) & \
                    (df_period['WSPD_DLM'] < USR)

    UTL = obs_4day['T500']-5
    UTR = obs_4day['T500']+5
    upper_500T_mask =   (df_period['T500'] > UTL) & \
                    (df_period['T500'] < UTR)

    SPL = obs_4day['P']-5
    SPR = obs_4day['P']+5
    qnh_mask =  (df_period['QNH'] > SPL) & \
            (df_period['QNH'] < SPR)

    STdL = obs_4day['Td']-5
    STdR = obs_4day['Td']+5
    td_mask = (df_period['Td'] > STdL) & \
          (df_period['Td'] < STdR)

    mask = steering_dir_mask&steering_spd_mask&upper_500T_mask&qnh_mask&td_mask

    num_of_TS_days = df_period.loc[mask,'any_ts'].sum()
    num_of_days_match_synop_pattern = \
            df_period.loc[mask].shape[0]

    if (num_of_days_match_synop_pattern > 0):

        if (num_of_TS_days > 0):
            duh = df_period.loc[mask,cols_display]
            # print(duh.sort_index())
            return (mask,duh,num_of_days_match_synop_pattern,num_of_TS_days)
            #return(num_of_TS_days/num_of_days_match_synop_pattern*100)
        else:
            # print("No matching TS days found")
            # calling function expects a tuple, can't help!!
            return (mask,None,num_of_days_match_synop_pattern,0)
    else:
        # print("No matching synoptic pattern in dataset")
        # calling function expects a tuple, can't help!!
        return (mask,None,-1,-1)



################################################################
'''MODIFY ABV FUNCTIONS to use sonde data upper air parameters
T500, Td500, wdir_500, wspd_500 for synoptic pattern matching
We can use EC Reanal or AR Reanal as well for upper data.
For those avlocs that have sonde flight, use that instead.

pandas.Series.dt.dayofyear grabs us The ordinal day of the year
df['date'].dt.dayofyear
pandas.DatetimeIndex.dayofyear
DatetimeIndex.dayofyear
storm_dates_ybbn_area.dayofyear

Use the calendar day of year to grab data across ALL years
for SAME period/season

input:
    sonde_date =  this is DAILY 00Z data (merged AWS and sonde)
    AWS is aws_data.resample('D')['AvID','Td','QNH','any_ts','AMP'].first(),
    sonde=sonde_data[['wdir500','wspd500','T500', 'lr850_500']],
    .rename(columns={'QNH': 'P','any_ts':'TS'})
period: default 6 weeks either side of given date
day   : date for which forecast is sought '''
#################################################################


def grab_data_period_centered_day_sonde(sonde_data,period=42, day=None):

    '''
    print('\nExtracting aws/sonde data for same seasonality or\
        \ncalendar days window:{} days either side of {}'\
            .format(period,period))
    '''
    # get dates for start/end of X weeks period centered on given date
    if (day): # IF
        start = pd.to_datetime(day) - pd.Timedelta(str(period) + ' days')
        end = pd.to_datetime(day) + pd.Timedelta(str(period) + ' days')
    else: #no date suppiled - use todays date
        start = pd.datetime.today() - pd.Timedelta(str(period) + ' days')
        end = pd.datetime.today() + pd.Timedelta(str(period) + ' days')

    # print ("start = {}, end = {}".format(start, end))

    # convert time period to day of year range
    day_range = pd.date_range(start=start,end=end,freq='D').dayofyear

    # grab sonde samples for specified calendar days/day of year only
    return (sonde_data.loc[sonde_data.index.dayofyear.isin(day_range)])

################################################################
'''Extract days with matching synop pattern and find how
many had TS. Fraction of matching synop days with storms
is proxy for storm potential.
inputs:
    obb_win: this is DAILY 00Z data (merged AWS and sonde)
    for a given calendar day period across several years
    obs_4day: observations close to 00Z for station
    for date for which TS forecast is sought
    For current day, grab the 00Z sonde and station 00Z sfc obs
    For future date, grab these fields from NWP. (Not yet coded!)'''
###################################################################
def calculate_percent_chance_ts_sonde(obb_win, obs_4day):


    print('\nSearching matched season records/days for synoptic condition matches....')

    # convert obs to series for dict like indexing
    # obs_4day = obs_4day.T.squeeze()

    '''
    Wind directions need special attention
    Normal Case:
        DIR between 30 and 330, can do normal +30/-30

    TWO  special cases
    CASE 1: wdir between 330 and 360
    say if wdir=350, wdir+30=380!!
    so here wdir=wdir+30-360 to get correct dir

    CASE 2: wdir between 0 and 30
    e.g. if wdir=10, wdir-30 = -20,-ve wind directiom
    so here wdir=wdir-30+360 to get correct dir'''

    if (obs_4day['wdir500'] >= 31) & (obs_4day['wdir500'] <= 329):
        UDL = obs_4day['wdir500']-30
        UDR = obs_4day['wdir500']+30
        steering_dir_mask = \
                (obb_win['wdir500'] >= UDL) & \
                (obb_win['wdir500'] <= UDR)

    elif (obs_4day['wdir500'] >= 330) & (obs_4day['wdir500'] <= 360):
        UDL = obs_4day['wdir500']-30
        UDR = obs_4day['wdir500']+30-360
        steering_dir_mask = \
                (obb_win['wdir500'] >= UDL) | \
                (obb_win['wdir500'] <= UDR)

    elif (obs_4day['wdir500'] >= 0) & (obs_4day['wdir500'] <= 30):
        UDL = obs_4day['wdir500']-30+360
        UDR = obs_4day['wdir500']+30
        steering_dir_mask = \
                (obb_win['wdir500'] >= UDL) | \
                (obb_win['wdir500'] <= UDR)
    else:
        print("No shit wind", obs_4day['wdir500'] )


    USL = obs_4day['wspd500']-10
    USR = obs_4day['wspd500']+10
    steering_spd_mask = (obb_win['wspd500'] > USL) & \
                        (obb_win['wspd500'] < USR)

    UTL = obs_4day['T500']-5
    UTR = obs_4day['T500']+5
    upper_500T_mask =   (obb_win['T500'] > UTL) & \
                        (obb_win['T500'] < UTR)

    SPL = obs_4day['P']-5
    SPR = obs_4day['P']+5
    qnh_mask =  (obb_win['P'] > SPL) & \
                (obb_win['P'] < SPR)

    STdL = obs_4day['Td']-5
    STdR = obs_4day['Td']+5
    td_mask = (obb_win['Td'] > STdL) & \
              (obb_win['Td'] < STdR)

    # middle 50% 5.5 to 6.5 for TS days,  5.0 to 6.0 for TS-free days
    # middle 50% 24 to 28 for TS days, 20 to 24 for non- TS days
    '''Better ability to discriminate than real lapse rate - we use this'''
    lr_mask = (obb_win['tmp_rate850_500'] > (obs_4day['tmp_rate850_500']-5)) & \
              (obb_win['tmp_rate850_500'] < (obs_4day['tmp_rate850_500']+5))

    # for pure temperature difference between 850 and 500
    #lr_mask = (obb_win['tmp_rate'] > (obs_4day['tmp_rate'] - 10)) & \
    #          (obb_win['tmp_rate'] < (obs_4day['tmp_rate'] + 10))

    print("Synop parameter thresholds\n500hPa wind DIR:\t{} and {} degrees\
          \n500hP wind SPD:\t\t{} to {} knots\n500hP Temp:\t\t{} to {} deg C\
          \nSLP:\t\t{} to {} hPa, \nsfc Td:\t\t{} to {} deg C\
          \nLapse Rate:\t\t{} to {} degC/km"
          .format(UDL, UDR, round(USL,1), round(USR,1),
                  round(UTL,1), round(UTR,1), SPL, SPR,
                  round(STdL,1),round(STdR,1),
          round(obs_4day['tmp_rate850_500']-5,1),
          round(obs_4day['tmp_rate850_500']+5),1))

    mask = steering_dir_mask & steering_spd_mask & \
           upper_500T_mask & qnh_mask & td_mask & lr_mask


    matching_synops = pd.DataFrame()  # empty df
    num_of_days_match_synop_pattern = np.nan
    num_of_TS_days = np.nan

    try:
        matching_synops = obb_win.loc[mask]
        '''num of days matching conditions is just number of
        days satisfying synop condition envelopes above'''
        #this can fail if no matchs
        num_of_days_match_synop_pattern = \
                matching_synops.shape[0]
    except:
        print("No matching synoptic days found in dataset")
        # exit - calling fn expected to deal with situation
        return (mask,matching_synops, # all NaNs except mask
                num_of_days_match_synop_pattern,num_of_TS_days)


    ''' for days satisfying synop conditions,count how many had TS
    'TS' is either True/1 or False/0   '''
    try:
        num_of_TS_days = matching_synops['TS'].sum()
    except:
        print("No TS days found in matching synops")
        return (mask,matching_synops,
                num_of_days_match_synop_pattern,num_of_TS_days)
                # only num_of_TS_days will be NaN

    # we get to here if no errors above, so no NaNs in return
    return (mask,matching_synops,
            num_of_days_match_synop_pattern,num_of_TS_days)


############################################################
def calculate_percent_chance_fg_sonde(obb_win:pd.DataFrame, obs_4day:pd.Series):

    # print(f'\nSearching matched season records/days for fog like conditions using these parameters\n{obs_4day}')
    '''
    obb_win  is data we are searching through - columns are
    ['AvID', 'T', 'Td','WS','WDir','QNH','fogflag','Station', 'level','900_wdir','900_WS']

    obs_4day is data we use for current day 00Z or 06Z data

    obs_4day['P'] = float(list(request.form.items())[0][1])
    obs_4day['T'] = float(list(request.form.items())[1][1])
    obs_4day['Td'] = float(list(request.form.items())[2][1])
    obs_4day['900Dir'] = float(list(request.form.items())[3][1])
    obs_4day['900spd'] = float(list(request.form.items())[4][1])
    '''

    if (obs_4day['900Dir'] >= 31) & (obs_4day['900Dir'] <= 329):
        UDL = obs_4day['900Dir']-30
        UDR = obs_4day['900Dir']+30

        steering_dir_mask = \
                (obb_win['900_wdir'] >= UDL) & \
                (obb_win['900_wdir'] <= UDR)
        print(f'900Hpa wind direction envelop:\t{obs_4day["900Dir"]} -->{UDL} to {UDR}')

    elif (obs_4day['900Dir'] >= 330) & (obs_4day['900Dir'] <= 360):
        UDL = obs_4day['900Dir']-30
        UDR = obs_4day['900Dir']+30-360

        steering_dir_mask = \
                (obb_win['900_wdir'] >= UDL) | \
                (obb_win['900_wdir'] <= UDR)
        print(f'900Hpa wind direction envelop:\t{obs_4day["900Dir"]} -->{UDL} to {UDR}')

    elif (obs_4day['900Dir'] >= 0) & (obs_4day['900Dir'] <= 30):
        UDL = obs_4day['900Dir']-30+360
        UDR = obs_4day['900Dir']+30

        steering_dir_mask = \
                (obb_win['900_wdir'] >= UDL) | \
                (obb_win['900_wdir'] <= UDR)
        print(f'900Hpa wind direction envelop:\t{obs_4day["900Dir"]} -->{UDL} to {UDR}')
    else:
        print("No shit wind", obs_4day['900Dir'] )
        # better set it to False - so match will fail - else will crash!!
        steering_dir_mask=False

    '''
    For fog - wind speeds does not look like strong discriminator
    # Percentage or Frequency of wind speeds bins
    33% of fog cases had 3000ft winds 0-10 knots
    50% of fog cases had 3000ft winds 10-20 knots
    14% of fog cases had 3000ft winds 20-30 knots, only 3% 30-40, 0% 40+
    > 83% of fog cases wind below 20 knots
    > 97% of fog cases wind below 30 knots
    For no fog cases
    29% of fog cases had 3000ft winds 0-10 knots
    47% of fog cases had 3000ft winds 10-20 knots
    20% of fog cases had 3000ft winds 20-30 knots, only 4% 30-40, <1% 40+
    > 85% of fog cases wind below 20 knots
    > 97% of fog cases wind below 30 knots '''

    USL = obs_4day['900spd']-10  # we changed range from +-10 to +-8
    USR = obs_4day['900spd']+10
    steering_spd_mask = (obb_win['900_WS'] > USL) & \
                        (obb_win['900_WS'] < USR)
    print(f'900Hpa wind speed envelope:\t{obs_4day["900spd"]:.1f} --> {USL:.1f} to {USR:.1f}')

    ''' SFC P not good at all to discriminate fog/no-fog days  - allow larger range '''
    SPL = obs_4day['P']-4 # we change range from +-5 to +-2
    SPR = obs_4day['P']+4
    qnh_mask =  (obb_win['QNH'] > SPL) & \
                (obb_win['QNH'] < SPR)
    print(f'QNH envelope:\t\t\t{obs_4day["P"]} --> {SPL:.1f} to {SPR:.1f}')

    ''' SFC T not good at all to discriminate fog/no-fog days - allow larger range
    STL = obs_4day['T']-4
    STR = obs_4day['T']+4
    t_mask = (obb_win['T'] > STL) & (obb_win['T'] < STR)
    print("SFC T: ", obs_4day['T'], STL,STR) '''


    STdL = obs_4day['Td']-3  # we change range from +-5 to +-2
    STdR = obs_4day['Td']+3
    td_mask = (obb_win['Td'] > STdL) & (obb_win['Td'] < STdR)
    print(f'SFC TD:\t\t\t\t{obs_4day["Td"]} --> {STdL:.1f} to {STdR:.1f}')

    #Need to check for low to mid moisture RH contribution
    #eg. k-index K index = (T850 - T500) + Td850 - (T700 - Td700)
    obb_win_TmTd =  obb_win['T'] - obb_win['Td']
    obs_TmTd     =  (obs_4day['T'] - obs_4day['Td'])
    TmTd_mask = (obb_win_TmTd > (obs_TmTd-3)) & (obb_win_TmTd < (obs_TmTd+3))
    print(f'SFC TmTd (+/- 3):\t\t{obs_TmTd:.1f} --> {(obs_TmTd-3):.1f} to {(obs_TmTd+3):.1f}')
    '''
    # middle 50% 6 to 8 for FG days,  8 to 12 for FGTS-free days
    # Better ability to discriminate than real lapse rate - we use this
    lr_low = obs_4day['lr_sfc_850']-3
    lr_up  = obs_4day['lr_sfc_850']+3
    lr_mask = (obb_win['lr_sfc_850'] > lr_low) & (obb_win['lr_sfc_850'] < lr_up)
    print(f'Lapse Rate:\t\t\t{obs_4day["lr_sfc_850"]:.1f} --> {lr_low:.1f} to {lr_up:.1f}')
    '''
    mask = steering_dir_mask & steering_spd_mask & qnh_mask & td_mask & TmTd_mask #& lr_mask #& t_mask
    matching_synops = pd.DataFrame()  # empty df
    num_of_days_match_synop_pattern = np.nan
    num_of_FG_days = np.nan

    try:
        matching_synops = obb_win.loc[mask]
        '''num of days matching conditions is just number of
        days satisfying synop condition envelopes above'''
        # print(matching_synops.index)
        # this can fail if no matchs
        num_of_days_match_synop_pattern = \
                matching_synops.shape[0]
        print(f'Num days matching synop pattern={num_of_days_match_synop_pattern}')
    except:
        print("No matching synoptic days found in dataset")
        # exit - calling fn expected to deal with situation
        return (mask,matching_synops, # all NaNs except mask
                num_of_days_match_synop_pattern,num_of_FG_days)


    ''' for days satisfying synop conditions,count how many had TS
    'TS' is either True/1 or False/0   '''
    try:
        print(matching_synops['fogflag'])
        print(matching_synops["fogflag"].value_counts())
        # num_of_FG_days = matching_synops.loc[matching_synops['fogflag']].sum() FAILS due NAN in fogflag
        # below ones work - so manage to get num fog days but for some reasons bombs so print never executes!!
        num_of_FG_days = matching_synops["fogflag"].value_counts()[1]
        num_of_FG_days = matching_synops.loc[matching_synops['fogflag']==True].shape[0]
        print(f'Num FG days found in matching synops={num_of_fog_days}')
    except:
        print("Did not find any FG days found in matching synops")
        return (mask,matching_synops,
                num_of_days_match_synop_pattern,num_of_FG_days)
                # only num_of_FG_days will be NaN

    # we get to here if no errors above, so no NaNs in return
    return (mask,matching_synops,
            num_of_days_match_synop_pattern,num_of_FG_days)


#############################################################
## Function to get TS start and end times for each day
'''
def get_ts_predictions() calls
--> def ts_stats_based_on_aws(aws_df, matched_ts_dates)
with a list of dates/days that had TS in matched synop days
which in turn calls this fn with aws observations
for days when had TS '''
#############################################################
def get_ts_start_end_duration(dat):

    '''Parameters:
    dataframe containing all observations that were classified
    as being "TS like"
    dataframe can even be all fog observations - all this fn does
    is for each day find the 1st obs, last obs and use that for simple
    duration calculation.
    returns: daily data with start, end and duration info for storms'''


    df=dat.copy()  #make copy as default is pass by reference

    ''' agg() NEEDs a column to work on!

    while resample('D') works on the datetime index
    built-in fn first/last need datetime like column,
    add 'time' col for easy aggregation
    .agg({'X':['sum','mean'],'Y':'max','Z':['min','std']})'''

    df['time'] = df.index
    '''
    print("\nFunction --> get_ts_start_end_duration(dat)\n",
          df[['WDir','WS','T','Td','QNH','date','any_ts','AMP']].head(1))
    '''
    df1 = df.resample('D')['time']\
            .aggregate(['first', 'last']).dropna()


    # calculate duration for TS each calendar day
    # taking diff of two datetimes yield timedelta obj
    df1['duration'] = round(\
    (df1['last'] - df1['first'] )/np.timedelta64(1, 'h'), 1)

    # get some other TAF forcast parameters
    # lowest vis and longest duration between 1 speci and next

    '''AWS (Automatic Weather Station) flag
    0 Manned    1 Automatic     2 Hybrid

    Note stations such as YAMB will be code 2 when manned
    and 1 when on AUTO - maybe we need list of stations
    like ['YAMB','YBOK','YTBL'] shud be treated as 2-hybrid
    even when flag is 1.'''
    #hybrid_sta_list = ['YBBN','YAMB','YBOK','YTBL','YBCS']
    #if sta in hybrid_sta_list:
    '''
    if (df.iloc[-1]['AWS_Flag'] == 2):
        df1['min_vis'] = df.resample('D')['vis']\
            .aggregate('min').dropna()
    elif (df.iloc[-1]['AWS_Flag'] == 1):
        df1['min_vis'] = df.resample('D')['vis_aws']\
            .aggregate('min').dropna()
    else:
        df1['min_vis'] = df.resample('D')['vis']\
            .aggregate('min').dropna()
    '''

    # hybrid stations cause issues from time to time
    # better use try except - so ensures at least one successful block
    try:
        # allways try with default vis first - if that fails tey vis_aws
        df1['min_vis'] = df.resample('D')['vis']\
            .aggregate('min').dropna()
    except:
        print("KeyError: Column not found: vis")
        df1['min_vis'] = df.resample('D')['vis_aws']\
            .aggregate('min').dropna()

    df1['max_gust'] = df.resample('D')['MaxGust10min']\
            .aggregate('max').dropna()

    df1['ttl_rain'] = df.resample('D')['pptn10min'] \
        .aggregate('sum').dropna()

    ''' THIS BIT NOT REALLY WORK WELL AT THE MOMENT
    # duration of each speci, min,max,mean
    # diff does val(n+1) - val(n), where n index
    df['time_diff'] = df['time'].diff()

    df2 = df.resample('D')['time_diff']\
            .aggregate(['min', 'max']).dropna()

    #df2['min'] = pd.datetime(df2['min'],"%H:%M")
    # df2['min'] = df2['min'].dt.get_total_hours()

    df2['min'] = df2['min']\
        .apply(lambda x: round(x / np.timedelta64(1, 'h')) )
    df2['max'] = df2['max']\
        .apply(lambda x: round(x / np.timedelta64(1, 'h')) )
    #df2['intervals'] = df.resample('D')['time_diff'].tolist()
    '''

    '''
    df2['min'] =df2['min']\
        .apply(lambda x: round(pd.Timedelta(x).total_seconds() \
                          % 86400.0 / 3600.0) )
    df2['min'] =df2['min']\
        .apply(lambda x: round(pd.Timedelta(x).total_seconds() \
                          % 86400.0 / 3600.0) )
    '''
    '''
    https://stackoverflow.com/questions/44864655/pandas-difference-between-apply-and-aggregate-functions
    https://stackoverflow.com/questions/21828398/what-is-the-difference-between-pandas-agg-and-apply-function
    '''
    # da = pd.concat([df1,df2],axis=1)
    # return (da)
    return(df1)



###############################################################
'''
Look up original AWS datafile with MATHCHNG synop days/dates that had TS
This should grab grab ALL (1/2 hourly) obs for matching synop days that had TS

Note

df.loc[(df.index.isin(new_dates)),:]   # doesn't quite cut it !!!
REF
https://stackoverflow.com/questions/48152584/how-to-filter-a-dataframe-of-dates-and-hours-by-a-list-of-dates


Note we can't do TS start and end times using this new subset dataframe
since get_ts_start_end_duration just grabs 1st and last obs from each day by default
W have to identify/label the TS obs/speci so it will then pick the 1st and last SPECI
for start and end times
aws['M-type']  is 'M' for routine Metar, 'S' for all SPECIS
'''
###############################################################

def ts_stats_based_on_aws(aws_df, matched_ts_dates):

    if len(matched_ts_dates) == 0:
        print("No TS days found in matching synops - so no stats")
        return (pd.DataFrame())

    # extract aws obs, ONLY for days in matching synop that had TS
    aws_4_ts_days = \
        aws_df.loc[(aws_df.index.floor('D').isin(matched_ts_dates))]
    # NB since index floored to day, Time data in index is dropped
    '''
    print("\nFunction --> ts_stats_based_on_aws(aws_df, matched_ts_dates)",
          aws_4_ts_days.shape,"\n", \
          aws_4_ts_days[['WDir','WS','T','Td','QNH','date','any_ts','AMP']].head(1))
    # mask using aws 'specis'/ or gpats count
    '''
    mask = (aws_4_ts_days['M_type'].str.contains('s')) | \
           (aws_4_ts_days['AMP'] > 0)

    if np.sum(mask) > 0:  # mask sum will show how many True!!
        ts_days_stats = get_ts_start_end_duration(aws_4_ts_days.loc[mask])
        ts_days_stats.index.name = 'Date'
        # ts_days_stats.reset_index().set_index(['Date','source'])
        return (ts_days_stats)
    else:
        print("No SPECI or lightning detected for TS days found - WIERDOOO.\
              \nInsufficient samples to generate statistics\
              \nThen how come found TS days in matched days!!!!")
        return (pd.DataFrame())  #empty dataframe


###############################################################
'''
Find percentage of matching synop days that had storms

input:
aws: aws data file from merge_aws_gpats_data(sta,aws_file)
Index(['AvID', 'M_type', 'pptn10min', 'pptn9am', 'T', 'Twb', 'Td', 'RH', 'VP',
       'SVP', 'WS', 'WDir', 'MaxGust10min', 'QNH', 'Ceil1_amnt', 'Ceil2_amnt',
       'Ceil3_amnt', 'Ceil1_ht', 'Ceil2_ht', 'Ceil3_ht', 'CeilSKCflag',
       'vis_aws', 'AWS_PW', 'AWS_PW15min', 'AWS_PW60min', 'AWS_Flag',
       'CAVOK_SKC_flag', 'RWY_ws_shear_flag', 'date', 'any_ts', 'AMP']

sonde: Brisbane sonde data, T,Td,wdir,wsp values at sfc, 850 and 500
Index(['P', 'Z', 'T', 'Td', 'wdir', 'wspd', 'P850', 'Z850', 'T850', 'Td850',
       'wdir850', 'wspd850', 'P500', 'Z500', 'T500', 'Td500', 'wdir500',
       'wspd500', 'tmp_rate', 'gpt_rate', 'lr850_500', 'LTM', 'day', 'season',
       'TS'],

period: how wide so seasonality match
14 days - 2 weeks wide, 28 is 4 weeks , 42 days is 6 weeks
my_date: date for which forecast is sought

makes these fn calls

search_window_obs =
        grab_data_period_centered_day_sonde(sonde,42,day)

mask,synop_match_obs,num_matches,ts_day_cnt =
       calculate_percent_chance_ts_sonde(search_window_obs, obs_4day)


matched = ts_stats_based_on_aws(aws,matched_ts_dates)
--> call made by abv fn
ts_days_stats = get_ts_start_end_duration(aws_4_ts_days.loc[mask])
'''
###############################################################



def get_ts_prediction(aws_sonde_daily,aws_data, period, my_date=None,obs_4day=None):

    matched = pd.DataFrame()  # empty dataframe-no TS found in matches

    station = aws_data.iloc[-1]['AvID']
    print("Searching archive for matching synop days for {}".format(station))
    print("Station aws Td, QNH merge with Brisbane sonde data\n",aws_sonde_daily.tail())

    if my_date:
        '''If date supplied - get prediction for that day'''
        print("Trying prediction for ",my_date)
        day = pd.to_datetime(my_date) #my_date ='2018-02-13'
        obs_4day = aws_sonde_daily.loc[my_date].T.squeeze()
    else:
        '''If no date supplied - get prediction for today'''
        print("No date given - will try predictions for today()")
        day = pd.datetime.today()
        obs_4day = obs_4day

    print("\nObs for day\n",obs_4day)

    # we can't have any missing values in search parameters
    if obs_4day[['wdir500','wspd500','T500', 'P','Td','tmp_rate850_500']].isnull().any():
        print("Fix Missing parameters First")
        return (pd.DataFrame())

    search_window_obs = \
        grab_data_period_centered_day_sonde(aws_sonde_daily,42,day)

    mask,synop_match_obs,num_matches,ts_day_cnt = \
        calculate_percent_chance_ts_sonde(search_window_obs, obs_4day)

    #print("num_matches,ts_day_cnt",num_matches,ts_day_cnt)

    if num_matches > 0:
        print('\nSearch window is:', len(search_window_obs),"days wide"\
        '\nNum days matching synop pattern in search window:',\
        len(synop_match_obs),mask.sum(),num_matches,\
        '\nNum days with TS in matching synop days:',ts_day_cnt)
        #mask,synop_match_obs
        #num_matches,ts_day_cnt
        # print(synop_match_obs.tail(1))
    else:
        print('\nlen(synop_match_obs) > 0:ELSE\
        \nNo matching days found from {} historical days.\
        \nMust have very unusual conditions!!!'\
                  .format(len(search_window_obs)))
        return (matched)

    if (ts_day_cnt >= 0):
        print("\nOut of {} days with matching synop pattern or environment\n\
        {} days had storms at {} airport.\nChance TS at {} = {}%"\
        .format(len(synop_match_obs),
        synop_match_obs['TS'].sum(),station,
        station,(synop_match_obs['TS'].sum()/len(synop_match_obs))*100))

        print('Num days with TS: ',synop_match_obs['TS'].sum(),
            'From matching synops:',synop_match_obs['TS'].shape[0])

        matched_ts_dates=(synop_match_obs[synop_match_obs['TS']>0].index)
        # print("1st method",matched_ts_dates)
        # 1st method DatetimeIndex(['2008-06-20'], dtype='datetime64[ns]', name='UTC', freq=None)
        print("\nMatching dates:", matched_ts_dates)

        matched = ts_stats_based_on_aws(aws_data,matched_ts_dates)
        return(matched)

    else:
        print('\nif (ts_day_cnt > 0):ELSE\nNo matching days found \
             \nfrom {} historical days. Must have very unusual conditions!!!'\
              .format(len(search_window_obs)))
        return (matched)


def get_ts_predictions_stations(stations,sonde2day=None,my_date=None):

    sonde_from_adams = ''
    print("\n\nProcessing TS prediction for station:{}".format(stations))
    import math

    '''on nginx server cur_dir causes issue !!!
    replacing it with app works with data direcroty moved under avguide/app/
    # cur_dir = os.path.dirname(__file__)
    # os.path.join(cur_dir,'data','sonde_hank_final.pkl'), 'rb'))
    '''
    day = None
    obs_4day=None
    predictions = []
    data = pd.DataFrame()

    # check set membership of stations  - for brisbane stations load Brisbane sonde
    # Empty containers are "false" (so empty set would be null/false) as are numeric values equivalent to zero
    # you can emplicityl test empty set using if len(myset)  <-- cardinality of the set
    if set(stations).intersection(set(['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY'])):
        # load Brisbane sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBBN_sonde_2300_aws.pkl'), 'rb'))
            #os.path.join('app','data','sonde_hank_final.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBBN','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR SEQ STATIONS\n",sonde_data.tail())
    elif set(stations).intersection(set(['YBRK','YGLA','YTNG','YBUD','YHBA','YMYB','YEML','YCMT','YMRB','YBMK','YBPN','YBHM'])):
        # load Rockhampton sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBRK_sonde_2300_aws.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBRK','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR CAPRICORN/CENTRAL HIGHLANDN COAST\n",sonde_data.tail())
    elif set(stations).intersection(set(['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL'])):
        sonde_data = pickle.load( open(
            os.path.join('app','data','YSSY_sonde_0300_aws.pkl'), 'rb'))
        print("\n\n\n\nBEGIN PROCESSING TS FORECASTS FOR SYDNEY BASIN\n",sonde_data.tail())

    '''
    We are matching storms based on 2300Z sonde data
    2300Z sonde data is actually data for following/next calendar day
    so we need to reindex the sonde data so we merge METAR 00Z data with correct days sonde data
    No such problems using sonde data after 2300Z - as in SYd case when sonde is 02 or 03Z
    as then METAR day 00Z and Sonde day both fall on the same date/day
    '''
    if set(stations).intersection(set(['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY'])):
        sonde_data.set_index(
            keys=(sonde_data.index.date + pd.Timedelta(str(1) + ' days')),
            drop=False,inplace=bool(1))
            # we loose datetime type of index in conversion above - restore BLW
        sonde_data.index = pd.to_datetime(sonde_data.index)

    # If date supplied - get TS predictions for that day
    # operationally - we wud always want predictions for today so my_date=''
    if my_date:
        day = pd.to_datetime(my_date)  # my_date is string like '2018-02-13'
    else:
        # If no date supplied - get prediction for TODAY
        day = pd.datetime.today()
        print("def get_ts_predictions_stations:\nNo date supplied-will try predictions for today", day)

    # CHECK 1ST TO SEE IF WE HAVE SONDE DATA
    # IF NONE - CAN'T DO PREDICTIONS
    if 'sonde_item' in session:
        # we need this default flag False - cause most of the time
        # manual entry is best - esp on python anywhere.com
        # DON'T REMARK  ELSE
        # if sonde_from_adams==0 : CODE BELOW FAILS !!!!
        sonde_from_adams = False
        # on BOM LAN sonde data is retrieved from adams - so not always the case
        # print("Houston - we have sonde data from adams", sonde_from_adams == True)
    else:
        # TRY GET SONDE DATA FROM ADAMS IN 1ST INSTANCE
        try:
            sonde = getf160_adams(40842)
            sonde = sonde.resample('D').apply(get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            '''further post processing -
            - adjust date (23Z issue!), drop extra STN_NUM columns
            - add day of year , season, drop duplicate rows for same date'''
            sonde = process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            #logger.debug("Todays sonde flight:", sonde2day)
            sonde_from_adams = True
            sonde2day =  sonde
            print("\n\nSonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams==True)
        except:
            print("\n\nHaving trouble getting radionsonde for",\
                day, "PLEASE ENTER SONDE DATA MANUALLY ", sonde2day)
            # FORCE USER TO ENTER SONDE DATA !!!!!!!!!!!!
            return redirect(url_for('sonde_update'))

    # WE DON'T PROCEED BELOW THIS LINE UNLESS HAVE SONDE DATA

    # now do predictions for all stations
    for station in stations:
        print("\n\nProcessing TS prediction for station:{} for {}"\
            .format(station,day.strftime("%Y-%m-%d")))
        # get station aws archive data
        df  = pickle.load(
                open(
                os.path.join('app','data', station+'_aws.pkl'), 'rb'))
        print(df[['AvID', 'WDir', 'WS', 'T', 'Td', 'QNH', 'any_ts', 'AMP']].tail(5))
        #print(df.index)
        #print(df.columns)
        #print(df.info)
        # merge with closest radiosonde upper data archive
        '''
        File "./app/__init__.py", line 1605, in storm_predict
        storm_predictions = bous.get_ts_predictions_stations(stations,sonde_data)
        File "./utility_functions_sep2018.py", line 3047, in get_ts_predictions_stations
        left = df.resample('D')[['AvID','Td','QNH','any_ts','AMP']].first(),
        ValueError: cannot reindex from a duplicate axis

        df.loc['2000-01-01':'2000-01-05'].between_time('00:00','00:30')
        can give more than one row for given date
        BUT if we resample to ('D') and rturn first() then gurantee only one row 
        and likely 00Z as well
        df.loc['2000-01-01':'2000-01-05'].between_time('00:00','00:30').resample('D').first()
        '''
        '''
        df_temp = None
        if utc == 0:
            df_temp = df.between_time('23:45', '00:15').resample('D').first()
            print("Matching using 10am data\n", df[['T', 'Td', 'QNH']].between_time('23:45', '00:15').tail(5))
        if utc == 2:
            df_temp = df.between_time('01:45', '02:15').resample('D').first()
            print("Matching using 12pm data\n", df[['T', 'Td', 'QNH']].between_time('01:45', '02:15').tail(5))
        if utc == 4:
            df_temp = df.between_time('03:45', '04:15').resample('D').first()
            print("Matching using 2pm data\n", df[['T', 'Td', 'QNH']].between_time('03:45', '04:15').tail(5))
        df_temp = df_temp.loc[:df.index.date[-1]]  # resample introduces days for rest of days in year!!
        # df_temp['fogflag'] = df_temp['fogflag'].astype(bool)  # force to be boolean converts NaN to False
        # Now this would work to filter fog days only ==>  df_temp[df_temp['fogflag']]
        '''
        # when we process all stations at once - assume match sought for 02Z/12pm 0bs
        # we may in future put a input for time n main page
        df_temp = df.between_time('01:45', '02:15').resample('D').first()
        aws_sonde_daily = pd.merge(
            # left = df.resample('D')[['AvID','Td','QNH','any_ts','AMP']].first(),
            left=df_temp[['AvID', 'WDir', 'WS', 'T', 'Td', 'QNH', 'any_ts', 'AMP']],
            right=sonde_data[['500_wdir', '500_WS', 'T500', 'tmp_rate850_500']],
            left_index=True, right_index=True, how='left') \
            .rename(columns={'QNH': 'P', 'any_ts': 'TS', '500_wdir': 'wdir500', '500_WS': 'wspd500'})
        print("\n\nMerged Sonde/AWS data is:\n", \
              aws_sonde_daily[['AvID', 'WDir', 'WS', 'T', 'Td', 'P','wdir500','wspd500']].tail(5))
        ''' get date input from main 'thunderstorm_predict.html' '''

        obs_4day = None

        if my_date:
            #If date supplied - get prediction for that day
            day = pd.to_datetime(my_date) #my_date is string like '2018-02-13'
            # get obs from station/sonde merged data for this date
            obs_4day = aws_sonde_daily.loc[my_date] #.T.squeeze()
            print("\n\nObservations for given date {} is \n{}"\
                .format(day.strftime("%Y-%m-%d"), obs_4day))
        else:
            #If no date supplied - get prediction for today
            day = pd.datetime.today()
            obs_4day = sonde2day  # initialise todays obs with todays sonde
            #print("Radio sonde for {} :\n{}"\
            #      .format(day.strftime("%Y-%m-%d"), obs_4day.to_frame()))
            try:
                '''Now we have already got todays sonde flight data,
                upper winds and temps and lapse rate info
                NEED to get station surface parameters from station obs'''

                wx_obs = get_wx_obs_www([station]).squeeze() #expects a list
                print("\n\nObservations for 00Z on {} for {} :\n{}"\
                    .format(day.strftime("%Y-%m-%d"), station, wx_obs.to_frame()))
                # extra work if call like this
                # wx_obs = get_wx_obs_www(stations)
                # sta_ob = wx_obs[wx_obs['name'].str.contains(station)]

                # update surface parameters from station aws data
                obs_4day['P'] = wx_obs['P']
                obs_4day['T'] = wx_obs['T']
                obs_4day['Td'] = wx_obs['Td']
                obs_4day['wdir'] = wx_obs['wdir']
                obs_4day['wspd'] = wx_obs['wspd']


                # when sonde data manually entered - we set these manually
                if sonde_from_adams==0 :
                    print("\n\nSonde flight from adams", sonde_from_adams)
                    obs_4day['T500'] = float(sonde2day['t500'])
                    obs_4day['wdir500'] = float(sonde2day['wdir500'])
                    obs_4day['wspd500'] = float(sonde2day['wspd500'])
                    obs_4day['tmp_rate850_500']  = \
                                    float(sonde2day['tmp_rate850_500'])
                else:
                    print("\n\nSonde flight data from adams will be used", sonde_from_adams)

                obs_4day['TS'] = None # we don't know if curr day had TS - silly!!

                logger.debug("Observations for today {} :\n{}"\
                    .format(day.strftime("%Y-%m-%d"), obs_4day))
            except:
                print("\n\nResults.html Having trouble getting station data for today\
                    \nTry predict TS using last obs in database")
                # obs_4day = aws_sonde_daily.loc[aws_sonde_daily.iloc[-1].index]
                continue

        if obs_4day[['wdir500','wspd500','T500', 'P','Td','tmp_rate850_500']].isnull().any():
            print("Fix Missing parameters First")

        ts_obs = obs_4day['TS']  #True class label for past dates
        num_days_synop = None
        search_window_obs = None
        synop_match_obs = None
        num_matches = None
        ts_day_cnt= None

        search_window_obs = \
        grab_data_period_centered_day_sonde(aws_sonde_daily,42,day)

        try:
            num_days_synop = len(search_window_obs)
        except:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No data in season windows: VERY RARE EVENT HAS HAPPENED")
            num_days_synop = 0


        mask,synop_match_obs,num_matches,ts_day_cnt = \
        calculate_percent_chance_ts_sonde(search_window_obs, obs_4day)

        print("num_matches,ts_day_cnt",num_matches,ts_day_cnt)

        if math.isnan(num_matches):
            proba = -1
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No matching synop days found from {} historical days.\
            \nMust have very unusual conditions!!!"\
                .format(len(search_window_obs)))


        if math.isnan(ts_day_cnt):
            proba = -1
            print("No TS days found in matching synops."\
                .format(len(search_window_obs)))


        if (ts_day_cnt > 0):
            num_matching_days = len(synop_match_obs)
            proba = ts_day_cnt*1.0/num_matching_days
        elif (ts_day_cnt == 0):  # no matching day had storms
            print("no matching day had storms")
            num_matching_days = len(synop_match_obs)
            proba = 0.0
        elif (ts_day_cnt == -1): # no matching days found - very unusual!!!!
            print("no matching days found - very unusual!!!!")
            ts_day_cnt = 0
            num_matching_days = 0
            proba = -1
        '''
        if (proba == -1):
            y = "thunderstorm prediction inconclusive"
        elif (proba >= .30):
            y = "thunderstorms almost certain"
        elif (proba >= .10):
            y = "thunderstorms likely"
        elif (proba < .04):
            y = "thunderstorms very unlikely"
        else:
            y = 'thunderstorms possible - 4 to 9% chance'
        '''

        pred = 'POSSIBLE' if ((proba >= 0.04) & (proba <= 0.1)) else ('LIKELY' if proba >= 0.10 else 'NO CHANCE ')

        if my_date:
            predictions.append([station, my_date,num_days_synop,
                                num_matching_days, ts_day_cnt,
                       round(proba * 100, 2),pred, ts_obs==1.0])
            data = pd.DataFrame(predictions)
            data.columns = \
            ['sta','date','synop_days','matches','ts_cnt','prob','pred','obs']
        else:
            predictions.append([station, day.strftime("%Y-%m-%d"),num_days_synop,
                                num_matching_days, ts_day_cnt,
                       round(proba * 100, 2),pred])
            data = pd.DataFrame(predictions)
            data.columns = \
            ['sta','date','synop_days','matches','ts_cnt','prob','pred']

            '''TS status will not be known for today!!!!'''
    return(data)


def get_fog_dates_adams(av_id = 'YBBN',get_dates_only=None):

    print("\n\nGetting fog days from ADAMS interface\n")

    conn = cx_Oracle.connect(user='anonymous', password='anonymous', dsn='adamprd')

    station = avid_adams[av_id]  # get adams station number
    '''To update fog dates need to get it from ADAMs'''
    start_date = '1900-01-01'
    end_date = pd.datetime.today().strftime("%Y-%m-%d")
    # station = 40842

    query = (
        "SELECT TO_CHAR(LSD, 'yyyy-mm-dd') AS Day, count(distinct decode(fog_flag,'Y',lsd))"
        "FROM SFC_DAYS WHERE "
        "LSD > TO_DATE('{start}', 'yyyy-mm-dd') AND LSD <= TO_DATE('{end}', 'yyyy-mm-dd') "
        " AND STN_NUM={station}"
        "GROUP BY TO_CHAR(LSD, 'yyyy-mm-dd')"
    ).format(
        start=start_date, end=end_date, station=station
    )

    df = sql.read_sql(query, conn, parse_dates=['DAY'], index_col='DAY')
    df.columns = ['fog_flag']
    df.sort_index(inplace=True, ascending=True)
    print(df.tail(20))

    # UTC fog date will be previous calender day
    fog_dates = df.index - pd.Timedelta('1 days')
    df.set_index(fog_dates, inplace=True)
    print(df.tail(20))

    # get only dates when had fog, so fog_flag is 1, 0 for no fog
    df = df.loc[df['fog_flag'] == 1]

    '''
    fog_data = pd.read_csv(
        open(os.path.join('app','data', 'fog_days_ybbn_since1980.csv'), 'rb'),
        parse_dates=['DAY'], index_col=['DAY'])

    # UTC fog date will be previous day
    fog_dates = fog_data.index - pd.Timedelta('1 days')
    fog_data.set_index(fog_dates,inplace=True)

    # get only dates when had fog
    fog_data = fog_data.loc[fog_data['fog_flag']==1]

    return (fog_data.index)'''

    return (df.index)

# https://stackoverflow.com/questions/40632750/whats-the-difference-between-enum-and-namedtuple
'''named tuples here are immutable sets - so the values for each of the tuple is
set of dates e.g. common fog dates in two different methods, set of disjoint dates etc
We can look up these dates in original tcz files for closer look
'''
from collections import namedtuple
vins_aut_vs_man = namedtuple(
    typename='vins_aut_vs_man',
    field_names='all_dates common_dates not_common auto_only man_only')
vins_vs_rob =     namedtuple(
    typename='vins_vs_rob',
    field_names='all_dates common_dates not_common vins_only robs_only')


# https://stackoverflow.com/questions/27841823/enum-vs-string-as-a-parameter-in-a-function

from enum import Enum
class compare_dates(Enum):
    auto_with_man = 1
    rob_with_vin = 2

'''
Python UDF User Defined FUnctions data type hints for arguments and return data types
see e-mail
'''
def compare_fog_dates(station:str='YBBN',how=compare_dates) -> namedtuple:
    """
    compare fog dates for same station from different source data sets
    performs various set algebra with found fog dates in the two data sources
    such as union/intersection/disjoint etc beween the set of fg_dates

    returns the various sets as a named tuple where each tuple value is a set of dates
    for given test - say dates common to both sets for set intersection

    Interesting that the manual and auto obs finds similar fog days
    set union = unique days from combined sets  <-- associative
    set intersection - dates in common i.e in both sets <-- associative
    set of dates which are common to all/both sets.

    set symmetric_difference - dates which are not common to both sets (associative)
    dates which appear in either one of the sets - not in both or intersection
    is like ( set_a.union(set_b) ).intersection(set_b)

    The set difference of A and B is a set of dates that exists only in set A but not in B
    This is not --> associative A.difference(B) not same as B.difference(A)

    Two sets are said to be disjoint sets if they have no common elements
    No reason to test for this! `set_a.isdisjoint(set_b)`

    Set A is said to be the subset of set B if all elements of A are in B
    A.issubset(B)

    print(f'how = {how}, compare_dates={compare_dates}, ,compare_dates.auto_with_man={compare_dates.auto_with_man},compare_dates.rob_with_vin={compare_dates.rob_with_vin}')
    """

    #if (how == compare_dates.auto_with_man):
    if (how.name=='auto_with_man'):
        fg_aut = get_fog_data_vins(station=station,auto_obs='Yep',get_dates_only="Yep")
        fg_man = get_fog_data_vins(station=station,auto_obs=None, get_dates_only="Yep")

        return vins_aut_vs_man(
        set(fg_aut).union(set(fg_man)),
        set(fg_aut).intersection(set(fg_man)),
        set(fg_aut).symmetric_difference(set(fg_man)),
        set(fg_aut).difference(set(fg_man)),
        set(fg_man).difference(set(fg_aut)))
    elif (how.name=='rob_with_vin'):
    # elif (how == compare_dates.rob_with_vin):
        # default case (how == compare_dates.rob_with_vin)
        fg_aut = get_fog_data_vins(station = station,auto_obs='Yep',get_dates_only=None)
        rob_dates = get_fog_data_robs_FCT(station=station,get_dates_only="Yep")
        # align my fog dates (first and last only) with Robs
        aut_dates = fg_aut.loc[fg_aut['fogflag']].loc[rob_dates[0]:rob_dates[-1]].index.date

        return vins_vs_rob(
        set(aut_dates).union(set(rob_dates)),
        set(aut_dates).intersection(set(rob_dates)),
        set(aut_dates).symmetric_difference(set(rob_dates)),
        set(aut_dates).difference(set(rob_dates)),
        set(rob_dates).difference(set(aut_dates)))


def get_fog_data_robs_FCT(station:str = 'YBBN',get_dates_only=None) ->namedtuple:
    """
    [Look up Roberts station fog summry files
    and get dates we had fog at the station. If get_dates_only is not None
    return the dates only, else return the fog data file]

    Keyword Arguments:
        station {str} -- [Aviation ID for station] (default: {'YBBN'})
        get_dates_only {[datetime]} -- [List of dates we had fog at Station] (default: {None})


    Returns:
        fg data {pandas dataframe} - if get_dates_only is None
        dates {datetime.date}      - list of dates we had fog at station
    """
    '''
    Now get fog info from Roberts QLD fog summary file
    We have option of generating these files on the fly as/if needed
    which would require calls to "sys" or "subprocess"

    Easiest fix for time being is have a script generate these files before hand
    in the app/data folder

    head -n 1 app/data/FogSummaryUnfiltered_QLD.csv > app/data/YBBN_fog_days_rob.csv
    awk -F',' 'BEGIN {IGNORECASE = 1} $2 ~ /ybbn/' app/data/FogSummaryUnfiltered_QLD.csv \
    | awk -F',' 'BEGIN {IGNORECASE = 1} $6 ~ /rain/' >> app/data/YBBN_fog_days_rob.csv
    '''

    print('Getting fog data for '+station+' derived using ROBS FCT')
    df_fg = pd.read_csv(os.path.join('app','data', station+'_fog_days_rob.csv'), parse_dates=[2,6,7,8,9])

    '''To get only YBBN 900 winds at 06Z
    head -n 1 UpperWinds_QLD.csv > ybbn_900_winds_06Z.csv ; awk -F',' 'BEGIN {IGNORECASE = 1} $1 ~ /ybbn/' UpperWinds_QLD.csv | awk -F',' '$4 ~ /900/'\
    | awk -F',' '$6 ~ /06:00:00/' >> ybbn_900_winds_06Z.csv

    df_winds = pd.read_csv(
        os.path.join('app','data', station+'_900_winds_06Z.csv',
        parse_dates=[5,10], index_col=[5] )
    '''
    # set fg onset dates as fog date
    # we dont need to correct fog dates as FG.onset date is UTC date on which 1st fog signal detected
    df_fg.index = df_fg['FG.onset'].dt.date # - pd.Timedelta(str(1) + ' days')
    #check #type(df_fg.index), type(df_fg.index[0])

    #df_fg.head(1)
    if get_dates_only:
        return df_fg.index
    else:
        return df_fg

def get_fog_data_vins(station:str='YBBN',auto_obs:str='Yes',get_dates_only:str=None)->pd.Index:
    """
    [Look up Vins station fog summary files
    and get dates we had fog at the station. If get_dates is not None
    return the dates only, else return the fog data file]

    Keyword Arguments:
        station {str} -- [Aviation ID for station] (default: {'YBBN'})
        get_dates_only {[datetime]} -- [List of dates we had fog at Station] (default: {None})

    Returns:
        {pandas.DataFrame}  - Dataframe if get_dates_only is None
        {pandas.Series}     - pd.Index.date, list of dates we had fog at station

    """
    # for fog stats derived using automatic observations data
    if auto_obs:
        fg = pd.read_csv(os.path.join('app','data', station+'2auto.csv'))
        print('Getting fog data for '+station+' derived using VINS auto obs matching')

        '''
        see perl script --> ./aws_format_v6.5_2020.pl
        if ( ($wind_SPD <= 10) &&   # to stop elevated spots like YTWB dropping fogs!!
    	 (($vis_obs <= 6)||($vis_aws <= 6)) && # ROB uses Vis<8km bigger NET!
    	 (($T-$Td) < 2) &&
    	 (($pptn10min < 0.1) && ($pptn_last < 0.1)) &&
         ((trim($aws_CL1A.$aws_CL1H) =~ /^(SCT|BKN|OVC)\s*[1-2]00$/)) )# NB fogs missed if no cld near gnd
        '''
    else:
        fg = pd.read_csv(os.path.join('app','data', station+'2manual.csv'))
        print('Getting fog data for '+station+' derived using VINS manual obs matching')
        '''
        if ( (($PW =~ /4[0-9]/) ||
    	  (trim($PW1) =~ /(PR|BC|VC|BL|DR)\s*FG/i) ||
    	  (trim($PW2) =~ /(PR|BC|VC|BL|DR)\s*FG/i) ||
    	  ($PW =~ /10/))
         # &&    (trim($aws_CL1A.$aws_CL1H) =~ /^(SCT|BKN|OVC)\s*[1-2]00$/)) # cld on gnd reqd condition
         && (($PW !~ /12/) &&  (trim($PW1) !~ /MI\s*FG/i))  # make sure no MIST(10) or MIFG(12)
         && ($pptn10min < 0.1)  # just sanity check - silly observer fog report rain 0.4mm 11/10/2019 20:00
         && (($T-$Td) < 2)
         && (($vis_obs < 10)||($vis_aws < 10)))  #sanity check - observer saying fog 13/06/2014 00:30 vis>10km
        '''
    fg.index = pd.to_datetime(
        fg['year'].astype(str) + fg['mon'].astype(str).str.zfill(2)+ \
        fg['day'].astype(str).str.zfill(2),format='%Y%m%d')

    fg.drop(['year', 'mon', 'day'], axis=1, inplace=bool(1))  # drop these for now
    # fg['fogflag'].values has spaces [' NO', ' YES', ' NO', ...]  > fix BLW
    fg['fogflag']= fg['fogflag'].str.replace(' ', '')
    fg['fogflag']=np.where(fg["fogflag"] == "YES", True, False) # make it boolean for easy filtering
    numeric_cols = ['rain24hr','min_vis', 'fg_onset', 'fg_finish','fg_duration',\
                    'Td5', 'Td8', 'Td11', 'Td14','QNH5', 'QNH8', 'QNH11', 'QNH14']
    fg[numeric_cols] = fg[numeric_cols].apply(pd.to_numeric, errors='coerce')
    # fg['rain_flag'] =  fg['rain24hr'] > 0.0 #same as below!
    fg['rain_flag'] = np.where(fg["rain24hr"]>0.0, True, False)
    # fg['fogflag'].groupby(fg['rain_flag']).value_counts() # group data by rain/no rain days and fog outcomes in each set
    # fg['fogflag'].groupby(fg['rain_flag']).value_counts(normalize=True) # get relative frequencies for each group

    fg_dates = pd.to_datetime(fg[fg['fogflag']].index.date)
    # fg[fg['fogflag']].index.isin(fg_dates).sum() #should return 287 fog days for YBBN
    if get_dates_only: # default is None:
        return (fg_dates)  # return only the fog dates for station
    else:
        return (fg) # return only actual fog stats dataframe


def get_climatological_fog_probability(station:str='YBBN',dates:[pd.datetime]=None,aws_sonde_daily=None):

    """[summary]

    Args:
        station (str, optional): [description]. Defaults to 'YBBN'.
        dates ([type], optional): dates = pd.date_range(start='2019-06-03' , end='2019-06-10', freq='D')
        aws_sonde_daily ([type], optional): [description]. Defaults to None.
    """
    stats = list()
    from collections import namedtuple
    matches = namedtuple(
        typename='matches',
        field_names='date num_of_fog_days num_of_days_match_synop_pattern')

    for date in dates:
        # date = date.strftime("%Y-%m-%d")  # no need!
        print(f'\nProcessing date:{date}')
        win=None
        win=grab_data_period_centered_day_sonde(aws_sonde_daily,35,date)
        if win is None:
            print("Empty window grab_data_period_centered_day_sonde()")
            next
        obs_4day = aws_sonde_daily.loc[date]
        # 'T','Td','900_wdir','900_WS','QNH'
        # if obs_4day.isnull().any()
        if (obs_4day.isnull()['T'] or obs_4day.isnull()['Td'] #or obs_4day.isnull()['lr_sfc_850']
            or obs_4day.isnull()['QNH'] or obs_4day.isnull()['900_wdir']
            or obs_4day.isnull()['900_WS']):
            print("Missing values for synop search parameters")
            next
        # just match columns names expected in called function - silly
        obs_4day = obs_4day.rename({'900_wdir':'900Dir','900_WS':'900spd','QNH': 'P'})
        mask,matching_synops,num_of_days_match_synop_pattern,num_of_FG_days=\
            calculate_percent_chance_fg_sonde(win,obs_4day)
        # print(f'num_of_FG_days={num_of_FG_days},num_of_days_match_synop_pattern={num_of_days_match_synop_pattern},chance={100*num_of_FG_days/num_of_days_match_synop_pattern}')
        #tmp = matches(date,num_of_FG_days,num_of_days_match_synop_pattern)
        stats.append(matches(date,num_of_FG_days,num_of_days_match_synop_pattern))
    return stats


###################################################################
def get_fg_predictions_stations_new(stations,sonde2day=None,my_date=None):
    """[summary]

    Arguments:
        stations {[list of strings]} -- [Stations/AviationIds for which TS predictionss are sought]

    Keyword Arguments:
        sonde2day {[pd.Series]} -- [Sounding data including 850 T/Td, 500 temps] (default: {None})
        my_date {[datetime]} -- [Date for which forecast is sough] (default: {None})
    """

    day = pd.datetime.today()
    print("\n\nProcessing FOG prediction for station:{}".format(stations))
    import math
    # cur_dir = os.path.dirname(__file__)

    # 1800Z data for airports - currently read from a csv file, index is airport ID like YBBN
    #['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB']:
    data_18Z = pd.read_csv(os.path.join('app','data', 'station_data_18Z.csv'), index_col=[1])
    predictions = []
    data = pd.DataFrame()

    # check set membership of stations  - for brisbane stations load Brisbane sonde
    # Empty containers are "false" (so empty set would be null/false) as are numeric values equivalent to zero
    # you can emplicityl test empty set using if len(myset)  <-- cardinality of the set
    if set(stations).intersection(set(['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY'])):
        # load Brisbane sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBBN_sonde_2300_aws.pkl'), 'rb'))
            #os.path.join('app','data','sonde_hank_final.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBBN','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR SEQ STATIONS\n",sonde_data.tail())
    elif set(stations).intersection(set(['YBRK','YGLA','YTNG','YBUD','YHBA','YMYB','YEML','YCMT','YMRB','YBMK','YBPN','YBHM'])):
        # load Rockhampton sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBRK_sonde_2300_aws.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBRK','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR CAPRICORN/CENTRAL HIGHLANDN COAST\n",sonde_data.tail())
    elif set(stations).intersection(set(['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL'])):
        sonde_data = pickle.load( open(
            os.path.join('app','data','YSSY_sonde_0300_aws.pkl'), 'rb'))
        print("\n\n\n\nBEGIN PROCESSING TS FORECASTS FOR SYDNEY BASIN\n",sonde_data.tail())

    # sonde_data = sonde_data.loc[:,['900_wdir', '900_WS','lr_sfc_850']].rename(columns={'900_wdir':'direction','900_WS':'speed'})
    sonde_data['lr_sfc_850'] = sonde_data['sfc_T']-sonde_data['T850']

    # now do predictions for all stations
    for station in stations:
        print("\n\nProcessing FG prediction for station:{}"\
            .format(station))
        # get station aws archive data for station
        df  = pickle.load(
                open(
                os.path.join('app','data', station+'_aws.pkl'), 'rb'))

        fg_aut=get_fog_data_vins(station=station,auto_obs='Yes')
        fg_dates = fg_aut.index.date
        sonde_data = pd.merge(left=sonde_data, right=fg_aut[['fogflag']],how='left',\
            left_index=True,right_index=True)
        #fg_dates = get_fog_data_vins(station = station,get_dates_only='Yes')
        # add fog flag columm to station aws data file
        #if station == 'YBBN':
        #    df.drop(['fogflag'], axis=1, inplace=bool(1))
        #df['date'] = df.index.date
        #df['fogflag'] = df['date'].isin(fg_dates)
        #print(stations, df['fogflag'].value_counts())

        # WE ONLY NEED TO MERGE THE 23Z WINDS ( 17Z flight woulf be better) WITH STATION DATA FILE

        # df_temp = df.loc[df.index.hour == 18]  # filter out 18Z obs from stations AWS obs data b4 merging in
        # df_temp = df.loc[np.logical_and(df.index.hour == 6, df.index.minute == 0)]
        # df_temp = df_temp.resample('D').first()  # gets only one 06XX UTC obs from each day
        df_temp = df.between_time('16:45','17:15').resample('D').first()
        df_temp = df_temp.loc[:df.index.date[-1]]  # resample introduces days for rest of 2020!!
        # note the above keeps 'fogflag' as bool but introduces some NaN which can make filtering paninful
        # df_temp['fogflag'] = df_temp['fogflag'].astype(bool)  # force to be boolean converts NaN to False
        # Now this would work to filter fog days only ==>  df_temp[df_temp['fogflag']]

        aws_sonde_daily = pd.merge(
            left=df_temp[['AvID', 'T', 'Td', 'WS', 'WDir', 'QNH']], \
            right=sonde_data[['900_wdir', '900_WS','lr_sfc_850','fogflag']], \
            # right=df_winds[['Station', 'level','900_wdir','900_WS']],\  #if using EC data file
            left_index=True, right_index=True, how='left')

        print("\n", aws_sonde_daily.tail(5))

        obs_4day = data_18Z.loc[station].copy()  # get station 1800/4am data
        print(obs_4day)
        # need to spilt 900 winds into dir and speed
        # SFC T, TD, and QNH good to go - obs_4day['P'], obs_4day['T'], obs_4day['Td']
        obs_4day['900Dir'] = int(obs_4day['WIND_900'].split('/')[0])
        obs_4day['900spd'] = int(obs_4day['WIND_900'].split('/')[1])
        # obs_4day['lr_sfc_850'] = int(obs_4day['lr_sfc_850'])

        print(obs_4day)

        ''' GET 18Z OBS FROM WEB SCRAPPING - DOES NOT WORK atm!
        wx_obs = get_wx_obs_www([station],18).squeeze()  # expects a list
        print("\nObservations for 18Z on {} for {} :\n{}" \
            .format(day.strftime("%Y-%m-%d"), station, wx_obs))
        # extra work if call like this
        # wx_obs = get_wx_obs_www(stations)
        # sta_ob = wx_obs[wx_obs['name'].str.contains(station)]

        # update surface parameters from station aws data
        obs_4day['P'] = wx_obs['P']
        obs_4day['T'] = wx_obs['T']
        obs_4day['Td'] = wx_obs['Td']
        obs_4day['wdir'] = wx_obs['wdir']
        obs_4day['wspd'] = wx_obs['wspd']

        print("\n18:00UTC obs from get_wx_obs\n", obs_4day)
        '''

        #fg_obs = obs_4day['FG']  #True class label for past dates
        num_days_synop = None
        search_window_obs = None
        synop_match_obs = None
        num_matches = None
        num_matching_days = None
        fg_day_cnt= None

        search_window_obs = \
        grab_data_period_centered_day_sonde(aws_sonde_daily,35,day)

        try:
            num_days_synop = len(search_window_obs)
        except:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No data in season windows: VERY RARE EVENT HAS HAPPENED")
            num_days_synop = 0


        mask,synop_match_obs,num_matches,fg_day_cnt = \
        calculate_percent_chance_fg_sonde(search_window_obs.copy(), obs_4day)

        print("num_matches,fg_day_cnt",num_matches,fg_day_cnt)

        if math.isnan(num_matches):
            proba = -1
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No matching synop days found from {len(search_window_obs)} historical days.\
            \nMust have very unusual conditions!!!')

        if math.isnan(fg_day_cnt):
            proba = -1
            print(f'No FG days found in {len(search_window_obs)} matching synops')

        if (fg_day_cnt > 0):
            num_matching_days = len(synop_match_obs)
            proba = fg_day_cnt*1.0/num_matching_days
        elif (fg_day_cnt == 0):  # no matching day had storms
            print("no matching day had fog")
            num_matching_days = len(synop_match_obs)
            proba = 0.0
        elif (fg_day_cnt == -1): # no matching days found - very unusual!!!!
            print("no matching days found - very unusual!!!!")
            fg_day_cnt = 0
            num_matching_days = 0
            proba = -1

        if (proba == -1):
            pred = "inconclusive"
        elif (proba >= .20):
            pred = "highly likely (PROB40 or ALT)"
        elif (proba >= .10):
            pred = "fog possible (PROB10 to PROB30)"
        elif (proba >= .05):
            pred = "slight chance fog (5% to 10% chance)"
        else:
            pred = 'fog unlikely'

        #pred = True if proba >= 0.15 else False
        predictions.append([station, day.strftime("%Y-%m-%d"),num_days_synop,
                    num_matching_days, fg_day_cnt,
                    round(proba * 100, 2),pred])
        data = pd.DataFrame(predictions)
        data.columns = \
        ['sta','date','synop_days','matches','fog_cnt','prob','pred']

    return(data)


def get_fg_predictions_stations(stations,sonde2day=None,my_date=None):
    """[summary]

    Arguments:
        stations {[list of strings]} -- [Stations/AviationIds for which TS predictionss are sought]

    Keyword Arguments:
        sonde2day {[pd.Series]} -- [Sounding data including 850 T/Td, 500 temps] (default: {None})
        my_date {[datetime]} -- [Date for which forecast is sough] (default: {None})
    """

    day = pd.datetime.today()
    print("\n\nProcessing FOG prediction for station:{}".format(stations))
    import math
    # cur_dir = os.path.dirname(__file__)

    # 1800Z data for airports - currently read from a csv file, index is airport ID like YBBN
    #['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB']:
    data_18Z = pd.read_csv(os.path.join('app','data', 'station_data_18Z.csv'), index_col=[1])

    predictions = []
    data = pd.DataFrame()

    # check set membership of stations  - for brisbane stations load Brisbane sonde
    # Empty containers are "false" (so empty set would be null/false) as are numeric values equivalent to zero
    # you can emplicityl test empty set using if len(myset)  <-- cardinality of the set
    if set(stations).intersection(set(['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY'])):
        # load Brisbane sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBBN_sonde_2300_aws.pkl'), 'rb'))
            #os.path.join('app','data','sonde_hank_final.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBBN','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR SEQ STATIONS\n",sonde_data.tail())
    elif set(stations).intersection(set(['YBRK','YGLA','YTNG','YBUD','YHBA','YMYB','YEML','YCMT','YMRB','YBMK','YBPN','YBHM'])):
        # load Rockhampton sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBRK_sonde_2300_aws.pkl'), 'rb'))
        #sonde_data = get_sounding_data('YBRK','2300')
        print("BEGIN PROCESSING TS FORECASTS FOR CAPRICORN/CENTRAL HIGHLANDN COAST\n",sonde_data.tail())
    elif set(stations).intersection(set(['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL'])):
        sonde_data = pickle.load( open(
            os.path.join('app','data','YSSY_sonde_0300_aws.pkl'), 'rb'))
        print("\n\n\n\nBEGIN PROCESSING TS FORECASTS FOR SYDNEY BASIN\n",sonde_data.tail())

    # The UTC date for sonde data is actually one less than the calendar data
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # very dodgy - fix logic!!!
    # depends on sonding time 17/19/23Z versus 02Z,04Z,05Z etc
    sonde_data.set_index(sonde_data.index - pd.Timedelta(str(1) + ' days'),inplace=bool(1))
    sonde_data = sonde_data[['P900', 'wdir900', 'wspd900', 'P850', 'wdir850', 'wspd850']] #only grab these cols
    sonde_data.rename(columns={'wdir900': '900_wdir','wspd900':'900_WS',\
            'wdir850': '850_wdir','wspd850':'850_WS'}, inplace = True)

    sonde_data['lr_sfc_850'] =  sonde_data['sfc_T']-sonde_data['T850']
    sonde_data = sonde_data[['lr_sfc_850','900_wdir','900_WS', 'T850','Td850','T700','Td700','T500','Td500']] #only grab these cols

    # now do predictions for all stations
    for station in stations:
        print("\n\nProcessing FG prediction for station:{}"\
            .format(station))
        # get station aws archive data for station
        df  = pickle.load(
                open(
                os.path.join('app','data', station+'_aws.pkl'), 'rb'))

        fg_dates = get_fog_data_vins(station = station,get_dates_only='Yes')
        # fg = get_fog_data_vins(station=station, auto_obs='YES')
        # df['fogflag'] = df['date'].isin(fg_dates)
        # add fog flag columm to station aws data file
        #if station == 'YBBN':
        #    df.drop(['fogflag'], axis=1, inplace=bool(1))

        snd = pd.merge(left=sonde_data, right=fg[['fogflag']], \
                       how='left', left_index=True, right_index=True)

        # WE ONLY NEED TO MERGE THE 23Z WINDS ( 17Z flight woulf be better) WITH STATION DATA FILE

        # df_temp = df.loc[df.index.hour == 18]  # filter out 18Z obs from stations AWS obs data b4 merging in
        # df_temp = df.loc[np.logical_and(df.index.hour == 6, df.index.minute == 0)]
        # df_temp = df_temp.resample('D').first()  # gets only one 06XX UTC obs from each day
        df_temp = df.between_time('07:45', '08:15').resample('D').first()
        df_temp = df_temp.loc[:df.index.date[-1]]  # resample introduces days for rest of days in year!!
        # note the above keeps 'fogflag' as bool but introduces some NaN which can make filtering paninful
        # df_temp['fogflag'] = df_temp['fogflag'].astype(bool)  # force to be boolean converts NaN to False
        # Now this would work to filter fog days only ==>  df_temp[df_temp['fogflag']]

        aws_sonde_daily = pd.merge(
            left=df_temp[['AvID', 'T', 'Td', 'WS', 'WDir', 'QNH']], \
            right=snd[['P900', '900_wdir', '900_WS', 'P850', '850_wdir', '850_WS','fogflag']], \
            # right=df_winds[['Station', 'level','900_wdir','900_WS']],\  #if using EC data file
            left_index=True, right_index=True, how='left')

        print("\n", aws_sonde_daily.tail(5))

        obs_4day = data_18Z.loc[station].copy()  # get station 1800/4am data

        # need to spilt 900 winds into dir and speed
        # SFC T, TD, and QNH good to go - obs_4day['P'], obs_4day['T'], obs_4day['Td']
        obs_4day['900Dir'] = int(obs_4day['WIND_900'].split('/')[0])
        obs_4day['900spd'] = int(obs_4day['WIND_900'].split('/')[1])

        print(obs_4day)

        ''' GET 18Z OBS FROM WEB SCRAPPING - DOES NOT WORK atm!
        wx_obs = get_wx_obs_www([station],18).squeeze()  # expects a list
        print("\nObservations for 18Z on {} for {} :\n{}" \
            .format(day.strftime("%Y-%m-%d"), station, wx_obs))
        # extra work if call like this
        # wx_obs = get_wx_obs_www(stations)
        # sta_ob = wx_obs[wx_obs['name'].str.contains(station)]

        # update surface parameters from station aws data
        obs_4day['P'] = wx_obs['P']
        obs_4day['T'] = wx_obs['T']
        obs_4day['Td'] = wx_obs['Td']
        obs_4day['wdir'] = wx_obs['wdir']
        obs_4day['wspd'] = wx_obs['wspd']

        print("\n18:00UTC obs from get_wx_obs\n", obs_4day)
        '''

        #fg_obs = obs_4day['FG']  #True class label for past dates
        num_days_synop = None
        search_window_obs = None
        synop_match_obs = None
        num_matches = None
        num_matching_days = None
        fg_day_cnt= None

        search_window_obs = \
        grab_data_period_centered_day_sonde(aws_sonde_daily,28,day)

        try:
            num_days_synop = len(search_window_obs)
        except:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No data in season windows: VERY RARE EVENT HAS HAPPENED")
            num_days_synop = 0


        mask,synop_match_obs,num_matches,fg_day_cnt = \
        calculate_percent_chance_fg_sonde(search_window_obs, obs_4day)

        print("num_matches,fg_day_cnt",num_matches,fg_day_cnt)

        if math.isnan(num_matches):
            proba = -1
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
            No matching synop days found from {len(search_window_obs)} historical days.\
            \nMust have very unusual conditions!!!')

        if math.isnan(fg_day_cnt):
            proba = -1
            print(f'No FG days found in {len(search_window_obs)} matching synops')

        if (fg_day_cnt > 0):
            num_matching_days = len(synop_match_obs)
            proba = fg_day_cnt*1.0/num_matching_days
        elif (fg_day_cnt == 0):  # no matching day had storms
            print("no matching day had fog")
            num_matching_days = len(synop_match_obs)
            proba = 0.0
        elif (fg_day_cnt == -1): # no matching days found - very unusual!!!!
            print("no matching days found - very unusual!!!!")
            fg_day_cnt = 0
            num_matching_days = 0
            proba = -1

        if (proba == -1):
            pred = "inconclusive"
        elif (proba >= .20):
            pred = "highly likely"
        elif (proba >= .10):
            pred = "fog possible"
        elif (proba >= .05):
            pred = "chance fog"
        else:
            pred = 'fog very unlikely'

        # pred = True if proba >= 0.15 else False
        predictions.append([station, day.strftime("%Y-%m-%d"),num_days_synop,
                    num_matching_days, fg_day_cnt,
                    round(proba * 100, 2),pred])
        data = pd.DataFrame(predictions)
        data.columns = \
        ['sta','date','synop_days','matches','fog_cnt','prob','pred']

    return(data)



def wind_quadrants(x):
    """
    Split winds into Quadrants
    Usage:
    df_new['wdir900_sector'] = df_new['900_wdir'].apply(wind_quadrants)

    :param x: wind direction series or values
    :return: quadrant direction
    """
    if ((x >= 0) & (x < 90)):
        return 'NE'
    elif ((x >= 90) & (x < 180)):
        return 'SE'
    elif ((x >= 180) & (x < 270)):
        return 'SW'
    elif ((x >= 270) & (x < 360)):
        return 'NW'
    else:
        return (np.NaN)

'''
Split winds into N/S or E/W semicircles
'''

def wind_semis_NS(x):
    if ((x < 90) | (x > 275)):
        return 'Nly'
    else:
        return 'Sly'

def wind_semis_EW(x):
    if ((x >= 0) & (x <= 180)):
        return 'Ely'
    else:
        return 'Wly'


'''
def classify(document):
    label = {0: 'negative', 1: 'positive'}
    X = vect.transform([document])
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    return label[y], proba

#The train function can be used to update the classifier given that a document and a class label
are provided.

def train(document, y):
    X = vect.transform([document])
    clf.partial_fit(X, [y])


@app.route('/results', methods=['POST'])
def results():
    form = ReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        review = request.form['moviereview']
        y, proba = classify(review)
        return render_template('results.html',
                                content=review,
                                prediction=y,
                                probability=round(proba*100, 2))
    return render_template('reviewform.html', form=form)


def get_knn_predictions(obs_4day):


    ######## Preparing the Classifier
    cur_dir = os.path.dirname(__file__)
    clf = pickle.load(open(os.path.join(cur_dir,
                 'pkl_objects',
                 'classifier.pkl'), 'rb'))
    db = os.path.join(cur_dir, 'reviews.sqlite')

    #Define a classify function to return the predicted class label as well
    as the corresponding probability prediction of a given text document.



    #import as pkl object previously trained KNN model
    knn = KNeighborsClassifier(n_neighbors=15)
    knn.fit(X_train, y_train)

    Now  and make prediction using this classifier

    print("Obs for day\n",obs_4day)
    cols = ['P','T', 'Td', 'wdir', 'wspd', 'T850', 'Td850',
      'wdir850', 'wspd850', 'T500', 'Td500', 'wdir500',
       'wspd500', 'tmp_rate850_500', 'day']
    obs_today = obs_4day[cols]
    print("Obs for prediction with KNN", obs_today)
    X = np.array(obs_today).reshape(1, -1)
    print("Input sample to KNN classifier", X)
    print("Prediction by KNN classifier is ---> ", knn.predict(X)[0])
'''



'''
find all dates where we had a positive match
then check whether the TS identification for given
days was based on gpats or aws data
also pick up onset, duration, end times for TS that day
'''

# find all dates where we had a positive match
# then check whether the TS identification for given
# days was based on gpats or aws data
# also pick up onset, duration, end times for TS that day

# matched_ts_dates = duf[duf['any_ts']].index
'''DatetimeIndex(['2014-01-03', '2017-01-21'], dtype='datetime64[ns]', freq=None)'''

'''If we use 'date' series to process '''
# matched_ts_dates = duf.loc[duf['any_ts'],'date'].dt.strftime("%Y-%m-%d")
# print(matched_ts_dates)
'''2014-01-03    2014-01-03
   2017-01-21    2017-01-21
Name: date, dtype: object'''''

# print(duf[duf['any_ts']].index.strftime("%Y-%m-%d"))
'''array(['2014-01-03','2017-01-21'],
      dtype='<U10')'''


## dewpoint given temp and RH
def dewpoint(temp,relhum):
    dewp = 243.04*(np.log(relhum/100)+((17.625*temp)/(243.04+temp)))\
          /(17.625-np.log(relhum/100)-((17.625*temp)/(243.04+temp)))
    return dewp

'''
Wind shear and lapse rate calculations from Bretts Scripts

$wind_shear_levels = array(
                array('sfc',850),
                array('sfc',700),
                array('sfc',500),
                array(850,500)
        );

//echo 'Shears:'."<br>\n";

echo '<tr><th class="sep" colspan="2">Shears<br />(kts)</th></tr>';

foreach ($wind_shear_levels as $wind_shear_level) {
        $speed1 = $wind_array['wind'][$wind_shear_level[0]][1];
        $speed2 = $wind_array['wind'][$wind_shear_level[1]][1];
        $dir1 = $wind_array['wind'][$wind_shear_level[0]][0];
        $dir2 = $wind_array['wind'][$wind_shear_level[1]][0];

        if($dir1 > $dir2) {
                $dir = $dir1 - $dir2;
        } else {
                $dir = $dir2 - $dir1;
        }

        $dir = $dir * 0.017453292519943295769236907684886; // in radians

        $shear = sqrt(($speed1*$speed1) + ($speed2*$speed2) - 2*($speed1)*($speed2)*cos($dir));
        $round_shear = round($shear);

        echo '<tr><td>'.$wind_shear_level[0].'-'.$wind_shear_level[1].'</td><td><strong>'.$round_shear.'</strong></td></tr>'."\n";

}

$lapse_rate_levels = array(
                array(850,500),
                array(700,500)
        );

echo '<tr><th class="sep" colspan="2">Lapse Rates<br />(&deg;C/km)</th></tr>';
foreach ($lapse_rate_levels as $lapse_rate_level) {
        $temp1 = $temp_array[$lapse_rate_level[0]]['temp'];
        $temp2 = $temp_array[$lapse_rate_level[1]]['temp'];
        $height1 = $temp_array[$lapse_rate_level[0]]['height'];
        $height2 = $temp_array[$lapse_rate_level[1]]['height'];
        $lapse_rate = ($temp1 - $temp2)/($height2 - $height1)*1000;

        echo '<tr><td>'.$lapse_rate_level[0].'-'.$lapse_rate_level[1].'</td><td><strong>'.number_format($lapse_rate,1).'</strong></td></tr>'."\n";
}


foreach ($feet_array as $feet) {
        $fzl_array[] = array($feet[1],$feet[3]);
}
if (is_numeric($fzl_array[2][1])) {

        echo '<tr><th class="sep" colspan="2">Heights<br />(ft)</th></tr>';
        $fzl = findTempLvl($fzl_array,0);
        $fzl = round($fzl,-2);
        $negtw = findTempLvl($fzl_array,-20);
        $negtw = round($negtw,-2);
        echo '<tr><td>FZL</td><td><strong>'.round($fzl,-2).'</strong></td></tr>'."\n";
        echo '<tr><td>-20&deg;C</td><td><strong>'.round($negtw,-2).'</strong></td></tr>'."\n";
}

echo '</table>';
'''


# convert compass direction to corresponding degrees
# see http://codegolf.stackexchange.com/questions/54755/convert-a-point-of-the-compass-to-degrees
def f(s):
    if 'W'in s:
        s = s.replace('N','n')
    a=(len(s)-2)/8
    if 'b' in s:
        a = 1/8 if len(s)==3 else 1/4
        return (1-a)*f(s[:-2])+a*f(s[-1])
    else:
        if len(s)==1:
            return 'NESWn'.find(s)*90
        else:
            return (f(s[0])+f(s[1:]))/2


'''
end_date = datetime.now()  #2017-04-04 13:56:54.789208
start_date = end_date - relativedelta(months=13)
date_range = pd.date_range(start_date, end_date, freq='M',closed=None)
'''
## explore http://pandas.pydata.org/pandas-docs/stable/timedeltas.html
## to fix not able to get correct month range
## https://chrisalbon.com/python/pandas_time_series_basics.html

## Python string formatters --> https://pyformat.info/
## http://www.diveintopython.net/native_data_types/formatting_strings.html

#print ('Number of arguments:', len(sys.argv), 'arguments.')
#print ('Argument List:', str(sys.argv))
#location = sys.argv[1]
#print('Weather forecasts for {}'.format(location.upper()))


def get_avlocs():
    import pandas as pd
    import os

    # "LOC_ID" "Location" "Lat"	"Long" "Elevation_ft" "Elevation" "HAM_Cld_ft" "HAM_Vis_m" "SAM_Cld_ft" "SAM_Vis_ft" "State"

    print( "Current directory from get_avlocs() in utility_fucntions_sept2018 is", os.getcwd())
    # Current directory from get_avlocs() in utility_fucntions_sept2018 is .  and pwd is  /mnt/win_data/shared/stats-R/flask_projects/avguide

    minima_path = os.path.join('app', 'static', 'minima_new.xls')
    # minima_path = os.path.join('static', 'minima_new.xls')
    with open(minima_path, 'rb') as m:
        locs = pd.read_excel(m, usecols=list(range(11)), header=0, index_col=0) #nrows=313, skiprows=list(range(10)))


    # ensure numeric data is forced to be numeric
    for col in ['Lat', 'Long', 'Elevation_ft', 'HAM_Cld_ft', 'HAM_Vis_m', \
                'SAM_Cld_ft', 'SAM_Vis_m']:
        locs[col] = pd.to_numeric(locs[col], downcast='integer', errors='coerce')

    # 'AREA' shud be an int not float, NaN is compatible with float but no int
    # columns in minima.xls can't be missing - drop rows with NaNs in these cols
    # else Raises ValueError: ('cannot convert float NaN to integer')
    locs.dropna(subset=['State', 'Location', 'HAM_Cld_ft', 'HAM_Vis_m'], inplace=True)

    # leave area as str as http://127.0.0.1:5000/api/v1/resources/tafors?area=40 fails!!
    # locs['AREA'] = locs['AREA'].astype(int)
    # locs['AREA'] = locs['AREA'].apply(lambda x: int(x) if x == x else np.NaN)

    decimals = pd.Series([4, 4], index=['Lat', 'Long'])  # lat/long to 4 dec plc
    locs = locs.round(decimals)

    # force convert text data to string
    cols_str = ['Location', 'Elevation', 'State']
    locs[cols_str] = locs[cols_str].astype(str)


    '''get PCA locs in diff states from pca file at web.bom.gov.au
    http://web.bom.gov.au/spb/adpo/aviation/LocationDatabase/pca.txt
    fixed width col format - so have to give width of each col, skips 1st and 3rd row
    only grab 1ST 2 COLS  usecols=[0,1]
    "LOC_ID" "AREA" "LOCATION_NAME" "Lat" "Long" "Type" "Reg" "State"'''
    pca_path = os.path.join('app','static', 'pca.txt')
    # pca_path = os.path.join('static', 'pca.txt')
    with open(pca_path, 'r') as p:
        pca = pd.read_fwf(p, widths=[7,5,33,10,11,5,4,5], skiprows=[0,2], usecols=[0,1], index_col=0)

    minima = locs#.reset_index()
    '''merge the two data sets into one dataframe
    https://pandas.pydata.org/pandas-docs/version/0.20/generated/pandas.read_fwf.html
    left join ensures we keep all airport minima info
    and supplment these with extra info from pca database, lat, long etc'''
    locs  = pd.merge(left=minima, right=pca, left_index=True, right_index=True, how='left')


    # 'AREA' shud be an int not float, NaN is compatible with float but no int
    # columns in minima.xls can't be missing - drop rows with NaNs in these cols
    # else Raises ValueError: ('cannot convert float NaN to integer')
    #             ValueError: cannot index with vector containing NA / NaN values
    locs.dropna(subset=['State','Location','HAM_Cld_ft', 'HAM_Vis_m','AREA'],inplace=True)

    # leave area as str as http://127.0.0.1:5000/api/v1/resources/tafors?area=40 fails!!
    # locs['AREA'] = locs['AREA'].astype(int)
    # locs['AREA'] = locs['AREA'].apply(lambda x: int(x) if x == x else np.NaN)

    # (x,y) coord system x is longitude , y is latitude

    return locs

def get_avlocs_old():

    import pandas as pd
    import os

    '''get TAF codes for airports in diff states from minima file at web.bom.gov.au
    http://web.bom.gov.au/spb/adpo/aviation/LocationDatabase/minima.xls
    "state" "Location" "Ident"  "HAM (cld (ft))" "HAM (vis (m))"
    "SAM (cld (ft))"  "SAM (vis (m))"   "MSA (ft)" '''
    minima_path = os.path.join(cur_dir,'static', 'minima.xls')
    with open(minima_path, 'rb') as m:
        minima = pd.read_excel(m, usecols=list(range(8)), skiprows=list(range(10)))

    '''get PCA locs in diff states from pca file at web.bom.gov.au
    http://web.bom.gov.au/spb/adpo/aviation/LocationDatabase/pca.txt
    fixed width col format - so have to give width of each col, skips 1st and 3rd row
    "LOC_ID" "AREA" "LOCATION_NAME" "Lat" "Long" "Type" "Reg" "State"'''
    pca_path = os.path.join(cur_dir,'static', 'pca.txt')
    with open(pca_path, 'r') as p:
        pca = pd.read_fwf(p, widths=[7,5,33,10,11,5,4,5], skiprows=[0,2])


    '''merge the two data sets into one dataframe
    left join ensures we keep all airport minima info
    and supplment these with extra info from pca database, lat, long etc'''
    locs  = pd.merge(left=minima, right=pca, left_on='Ident', right_on='LOC_ID', how='left')\
            .drop(['state','Ident','LOCATION_NAME'], axis=1)\
            [['LOC_ID', 'AREA', 'Lat', 'Long', 'Type','Reg', 'State',\
            'Location','HAM (cld (ft))', 'HAM (vis (m))', \
            'SAM (cld (ft))','SAM (vis (m))', ' MSA (ft)']]\
            .set_index('LOC_ID')

    cols_flt = ['Lat', 'Long','HAM (cld (ft))', 'HAM (vis (m))', \
            'SAM (cld (ft))','SAM (vis (m))', ' MSA (ft)']

    # ensure numeric data is forced to be numeric
    for col in  ['Lat', 'Long', 'HAM (cld (ft))', 'HAM (vis (m))', \
            'SAM (cld (ft))','SAM (vis (m))', ' MSA (ft)']:
        locs[col] = pd.to_numeric(locs[col], downcast='integer',errors='coerce')

    # 'AREA' shud be an int not float, NaN is compatible with float but no int
    # columns in minima.xls can't be missing - drop rows with NaNs in these cols
    # else Raises ValueError: ('cannot convert float NaN to integer')
    locs.dropna(subset=['State','Location','HAM (cld (ft))', 'HAM (vis (m))'],inplace=True)

    # leave area as str as http://127.0.0.1:5000/api/v1/resources/tafors?area=40 fails!!
    # locs['AREA'] = locs['AREA'].astype(int)
    # locs['AREA'] = locs['AREA'].apply(lambda x: int(x) if x == x else np.NaN)

    decimals = pd.Series([4,4],index=['Lat', 'Long'])  # lat/long to 4 dec plc
    locs = locs.round(decimals)

    # force convert text data to string
    cols_str = ['AREA','Location', 'Type', 'Reg', 'State']
    locs[cols_str] = locs[cols_str].astype(str)

    # (x,y) coord system x is longitude , y is latitude
    # shorten longer names
    locs.rename(columns= {
         'HAM (cld (ft))':'HAM_cld_ft', 'HAM (vis (m))':'HAM_vis_m', \
         'SAM (cld (ft))':'SAM_cld_ft','SAM (vis (m))':'SAM_vis_m', ' MSA (ft)':'MSA'}, inplace=True)

    return locs


def get_wx_obs_www(stations, hist=''):
    stations_all = []   # list to store each station as they are created
    #['YAMB','YBBN','YBAF','YBSU','YBCG','YTWB','YBOK']
    print(stations)
    area = "SE QLD"
    for airport in stations:

        # avid_wmo_dict = {'YBBN':94578,'YBAF':94575,....}
        # avid to climate station numbers
        station = avid_wmo_dict[airport]
        if airport in nt:
            url = "http://www.bom.gov.au/fwo/IDD60801/IDD60801.{}.json".format(station)
        if airport in wa:
            url = "http://www.bom.gov.au/fwo/IDW60801/IDW60801.{}.json".format(station)
        if airport in nsw:
            url = "http://www.bom.gov.au/fwo/IDN60901/IDN60901.{}.json".format(station)
            if airport=='YSHL':
                url = "http://www.bom.gov.au/fwo/IDN60701/IDN60701.{}.json".format(station)
        if airport in vic :
            url = "http://www.bom.gov.au/fwo/IDV60901/IDV60901.{}.json".format(station)
        if airport in sa:
            url = "http://www.bom.gov.au/fwo/IDS60901/IDS60901.{}.json".format(station)
        if airport in qld:
            url = "http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.{}.json".format(station)


        print ("Fetching {} observations from {}".format(airport,url))
        obs_response = requests.get(url)
        obs_json = json.loads(obs_response.text)
        stations_all.\
        append( \
               pd.DataFrame( obs_json['observations']['data'], \
                 columns = ['sort_order' , 'wmo', 'name', 'history_product', \
                             'local_date_time', 'local_date_time_full', 'aifstime_utc', \
                             'lat', 'lon', 'apparent_t', 'cloud', 'cloud_base_m', 'cloud_oktas', \
                             'cloud_type', 'cloud_type_id', 'delta_t', 'gust_kmh', 'gust_kt', 'air_temp', 'dewpt', \
                             'press', 'press_msl', 'press_qnh', 'press_tend', 'rain_trace', 'rel_hum',\
                             'sea_state', 'swell_dir_worded', 'swell_height', 'swell_period', \
                             'vis_km', 'weather', 'wind_dir', 'wind_spd_kmh', 'wind_spd_kt']))

    df = pd.concat(stations_all)    # join all the stations together
    list_to_drop = ['sort_order' , 'history_product', 'local_date_time', 'local_date_time_full','lat', 'lon', 'apparent_t',\
                 'cloud_type', 'cloud_type_id', 'delta_t', 'gust_kmh', 'press', 'press_msl', 'press_tend',\
                 'sea_state', 'swell_dir_worded', 'swell_height', 'swell_period', 'wind_spd_kmh']

    df.drop( list_to_drop, axis='columns',inplace=True)

    # U can also drop by column int positions
    # cols_drop = [0,3,4,5,7,8,9,13,14,15,16,20,21,23,26,27,28,29,33]
    # df.drop(df.columns[cols_drop],axis=1,inplace=True)

    # abbreviate some of the longer column names .e.g 'air_temp' -> 'T', 'dewpt'->'Td' etc
    df.rename( columns= {'name':'av_id','cloud_base_m': 'cld_base', 'cloud_oktas': 'cld_okta', 'gust_kt':'gust',\
                     'air_temp':'T', 'dewpt':'Td','press_qnh':'QNH', 'rel_hum':'RH',\
                     'vis_km':'vis', 'wind_dir':'dir', 'wind_spd_kt':'spd'}, inplace=True)

    # df.sort_values(by='aifstime_utc', ascending=True,inplace=True)
    # we postpone this to after set_index

    for col in  ['QNH','T', 'Td','spd','gust', 'RH','vis']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # convert text data to string
    # df[cols_str] = df[cols_str].astype(str)

    # Convert df['aifstime_utc'] from string to datetime
    df['date'] = pd.to_datetime(df['aifstime_utc'])

    # Set df['date'] as the index and delete the column
    df.set_index(keys='date', drop=True, inplace=True)
    # localise UTC time to local time
    # df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert('Australia/Brisbane')

    '''drop 'date' column at same time
    also need to drop column 'aifstime_utc'
    df.drop(['date', 'aifstime_utc'], axis=1, inplace=True)  '''

    df.drop(['aifstime_utc'], axis=1, inplace=True)
    df.sort_index(axis=0,ascending=True,inplace=True)  #sort index ascending


    df.cld_base = df.cld_base * 3.28084    #convert cloud base m to ft
    #df['dir'] = df['dir'].apply(f)

    cols_display = ['av_id','QNH','T', 'Td','dir','spd','gust', 'RH','vis']#,'cld_okta','cld_base']
    df = df[cols_display]

    # TypeError: Empty 'DataFrame': no numeric data to plot, when plotting
    # columns had values 'None' , if convert to NaN, plot() won't complain!!

    # df.isnull()   --> True for many columns with values 'None'
    # for some reason these None values are not treated same as NaN
    # so replace python None with pandas NaN

    df.fillna(value=np.nan, inplace=True)

    # fix wind direction
    # df['dir'] = df['dir'].apply(f)

    # change station names to av IDs

    if (area == "SE QLD"):
        name_dict = {'Amberley':'YAMB', 'Archerfield':'YBAF',
             'Brisbane Airport':'YBBN' , 'Coolangatta':'YBCG',
             'Oakey':'YBOK' ,'Sunshine Coast Airport':'YBSU',
             'Toowoomba':'YTWB', 'Charleville':'YBCV','Roma':'YROM',
             'St George':'YSGE', 'Thargomindah':'YTGM','Ballera':'YLLE',
             'Windorah':'YWDH','Birdsville':'YBDV'}
        df['av_id'] = df['av_id'].map(name_dict)


    df_hist = df
    df_today = pd.DataFrame()

    # dump csv to "/tmp/area40_observations.csv"
    # df.to_csv("/tmp/Oct17_2017_area40_observations.csv", sep=',', header=True, index=True)

    # get todays observations - now since we use UTC time today starts from 00UTC/10am
    # try first to avoid KeyError: 'the label [2018-06-23] is not in the [index]'
    # after 14UTC, local today is day+1, so get yesterdays 00Z in that case

    try:
        df_today = df.loc[datetime.today().strftime('%Y-%m-%d'), cols_display]
        print("Todays ({}) obs for {}:\n{}"\
              .format(datetime.today().strftime('%Y-%m-%d'),area, df_today.between_time('0:0', '1:0')))
        # df.iloc[np.lexsort((df.index, df.A.values))] # Sort by A.values, then by index
        # when we print(df_today.index) the indices still contain full datetime
        # we only wud like the 00Z obs
    except:
        yesterday = datetime.today() - relativedelta(days=1)
        df_today = df.loc[yesterday.strftime('%Y-%m-%d'), cols_display]
        print("Yesterdays ({}) obs for {}:\n{}" \
              .format(yesterday.strftime('%Y-%m-%d'), area, df_today.between_time('0:0', '1:0')))
        '''We get times that are not between two times by setting start_time later than end_time
        This effectively drops all obs 01Z till 23Z
        date                 name     QNH     T   Td  dir  spd  RH vis
        2018-06-22 00:00:00  YBBN  1026.9  17.8  8.9  SSW    9  56  10
        2018-06-22 00:30:00  YBBN  1026.9  18.9  9.1  SSW    9  53  10
        2018-06-22 01:00:00  YBBN  1026.6  20.2  9.2    S    8  49  10
        2018-06-22 23:00:00  YBBN  1026.2  14.9  8.5  SSW   11  65  40
        2018-06-22 23:30:00  YBBN  1026.2  15.4  8.2  SSW   13  62  10
        '''

    if hist:
        df_10am = df_hist
    else:
        df_10am = \
            df_today.loc[
                np.logical_and(
                    df_today.index.hour == 0,
                    df_today.index.minute == 0)]

        # df_10am = df_today.loc[df_today.index.hour == 0,cols_display]
        # df_10am = df_10am.sort_values(by=['av_id'], ascending=[True])
        # print("Row with duplicate av IDs", df_10am['name'].duplicated().sum())
        # print(df_10am['name'].duplicated())
        # drop duplicates
        df_10am = df_10am.loc[~df_10am['av_id'].duplicated(keep='first'), :]
        # see https://www.ritchieng.com/pandas-removing-duplicate-rows/
        # pandas.DataFrame.drop_duplicates has issues !!!!
        # df_10am.drop_duplicates(subset='Name', keep='first',inplace=True)

    df_10am.columns = ['av_id', 'P', 'T', 'Td', 'wdir', 'wspd', 'gust', 'RH', 'vis']
    print ("Fetched {} observations".format(airport))
    print(df_10am.tail())

    return (df_10am.sort_index(axis=0))



def get_airport_metar_speci(avid):

    """
    Grab METARAWS file for given aviation location and find and SPECIS
    """
     # now get any SPECIS
    '''
    metar_url = (
        'http://aifs-qld.bom.gov.au/cgi-bin/uncgi-bin/metar_hist/?{}').format(avid)
    metar_response = requests.get(metar_url)    '''

    # now get any SPECIS using WMO ids from
    # Problem with these is that obs that are SPECIS are not tagged with 'SPECI' keyword
    # Brets perl code was removing SPECI, METAR from AWS data, he has allowed that to report now - so good to use

    metar_url = 'http://aifs-qld.bom.gov.au/cgi-bin/local/qld/rfc/bin/metar_disp.pl'
    payload = {'WMO': avid_wmo_dict[avid]}
    metar_response = requests.get(metar_url, params=payload)

    print (metar_response.url)  #check if url formed correctly

    #metar_url ='http://aifs-qld.bom.gov.au/cgi-bin/local/qld/rfc/bin/metar_disp.pl?WMO={}'\
    #                .format(avid_wmo_dict[avid])
    #metar_response = requests.get(metar_url)

    print (metar_response.status_code)
    if (metar_response.status_code == requests.codes.ok):
        print ("Found file resource")
        print (metar_response.headers.get('content-type'),"\n")

    # print(metar_response.text)   will prints entire file

    # save response file so we can search it later for SPECIS
    with open('/tmp/metadata.txt', 'wb') as f:
        f.write(metar_response.content)

    f = open('/tmp/metadata.txt', 'r')

    # no matches will simply return an empty list
    matches = re.findall(r'SPECIAWS', metar_response.text)
    # http://www.pitt.edu/~naraehan/python3/re.html

    # replace all `&nbsp;` with 1 space

    if (len(matches) > 0):
        print ("\n\nSpecis for {}".format(avid), "\n#################")
        # now step through each metar and print out if its SPECI
        for line in f:
            if 'SPECIAWS' in line:
                print (cleanhtml(line.replace('&nbsp;',' ')))
                #if (avid == 'YBHM'):   # special case YBHM - print 2nd line as well
                #    print (next(f))    # as 1st line only upto RMK
    else:
        print("No specis for {}".format(avid), "\n------------------")

'''
    end_date = datetime.now()  #2017-04-04 13:56:54.789208
    start_date = end_date - relativedelta(days=2)
    #date_range = pd.date_range(start_date, end_date, freq='M',closed=None)


    # we try 3 differrent ways to call the plot method
    # plot() by default uses the dataframe index for x-axis, hence no x= ...
    df.loc[ start_date:end_date, ['spd', 'gust']]\
    .plot(title="{} Airport Plots".format(avid))
    plt.ylabel('knots')

    df.loc[ start_date:end_date,['T', 'Td']].plot()
    plt.ylabel('Degrees C')

    df.loc[ start_date:end_date].plot(y=['dir1'], style='r.')
    plt.ylabel('Degrees')

    df.loc[ start_date:end_date].plot(y=['QNH'])
    plt.ylabel('QNH Pressure (hPa)')

    df.loc[ start_date:end_date, ['cld_base', 'cld_okta']].plot(subplots=True)

    plt.show()
'''


def get_precis(myloc=None):

    import pandas as pd
    import wget
    import os
    import requests
    import urllib
    from xml.dom import minidom
    import xml.etree.ElementTree as etree


    def xtoDF(link):
        xml = urllib.request.urlopen(link)
        # xml = urllib.urlopen(link)
        dom = minidom.parse(xml)
        locs = []

        forecasts = dom.getElementsByTagName('forecast')[0]
        for area in forecasts.getElementsByTagName('area'):
            atts = area.attributes
            if atts['type'].value == 'location':
                locs.append({
                    'name': atts['description'].value,
                    'aac': atts['aac'].value,
                })
        return pd.DataFrame(locs)


    def get_preci_forecasts(loc,tree):

        # get list of all <area> element tags - some 180 to 240 preci locations!!
        lists = (tree.findall("forecast/area"))
        #print("\n\n\nlists",lists)

        for item in lists:
            # find matching town or location
            if (loc.lower() in item.attrib['description'].lower()):
                try:
                    time = (item.findall("forecast-period"))
                    #print("\n\ntime",time)
                    time = time[0].attrib['start-time-local']
                    #print("\n\ntime",time)
                except:
                    pass

                # print ("\n\n###############################################################\n")
                # print ("Forecast for:\t {} issued at:\t {}"(format(item.attrib['description']), format(time)))
                # print ("\nForecast for ", item.attrib['description']," issued at:" , time,"\n")
                # print(item.attrib)

                fcst_param_list = []

                for day in item.iter('forecast-period'):
                    fcst_dict = {}
                    # print ("\nForecasts for day:\t\t", day.attrib['start-time-local'])
                    for item in day.findall('element'):
                        # print (item.get('type'),":\t\t", item.text)
                        fcst_dict.update({item.get('type'): item.text})

                    for item in day.findall('text'):
                        # print (item.get('type'),":\t\t", item.text)
                        fcst_dict.update({item.get('type'): item.text})

                    fcst_dict.update({'date_time': day.attrib['start-time-local']})
                    fcst_param_list.append(fcst_dict)

                # print(fcst_param_list)
                return (pd.DataFrame.from_dict(data=fcst_param_list, orient='columns'))

            else:
                # print("Preci loc not found")
                # break  # DONT - GO TO NEXT ITEM!!
                continue

    # Grab all preci XML files and parse the tree
    qld_tree=None
    nt_tree=None
    wa_tree=None
    nsw_tree=None
    vic_tree=None
    sa_tree=None
    for i,state in enumerate(['qld','nt','wa','nsw','vic','sa']):
        if i==0:    # if state=='qld'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            qld_tree = etree.parse(xml)
        if i==1:    # if state=='nt'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDD10207.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            nt_tree = etree.parse(xml)
        if i==2:    # if state=='wa'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDW14199.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            wa_tree = etree.parse(xml)
        if i==3:    # if state=='nsw'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDN11060.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            nsw_tree = etree.parse(xml)
        if i==4:    # if state=='vic'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10753.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            vic_tree = etree.parse(xml)
        if i==5:    # if state=='sa'
            preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDS10044.xml'
            print('Processing ' + state)
            #preci_locations = xtoDF(preci_url)
            #print(preci_locations.head())
            xml = urllib.request.urlopen(preci_url)
            sa_tree = etree.parse(xml)

    # Now grab preci forecasts for all aviation locations we need precis for
    # these locations are defined in avid_preci dictionary
    preci_df_list = []
    for avid,location in avid_preci.items(): # for our specified aviation locations
        print('\n\nWeather forecasts for avid:{}-->{}'.format(avid,location.upper()))
        if avid in qld:
            tree = qld_tree
        elif avid in nt:
            tree = nt_tree
        elif avid in wa:
            tree = wa_tree
        elif avid in nsw:
            tree = nsw_tree
        elif avid in vic:
            tree = vic_tree
        elif avid in sa:
            tree = sa_tree
        else:
            print("Shit  YTST-->KALUMBURU YFDF-->PARABURDOO")
        preci_df = get_preci_forecasts(location,tree) # avid_preci[location],tree)

        # convert day into datetime index object - so we can index by datetime
        if preci_df is None:
            pass
            print("location is Nonetype - No preci found for either Christmas and Cocos and Barimunya!!!")
        else:
            preci_df['location'] = location
            try:
                preci_df['date_time'] = \
                preci_df['date_time'].str.extract(r'(\d{4}-\d{2}-\d{2})', expand=True)
                preci_df['date_time'] = pd.to_datetime(preci_df['date_time'], errors='coerce')
            except:
                print(f'Some errors in processing {avid}:{location}')
                pass
            preci_df_list.append(preci_df)

    # preci_df_tmp.append(pd.concat(preci_df_list))

    preci_df = pd.concat(preci_df_list)

    # abbreviate some of the longer column names .e.g 'air_temp' -> 'T', 'dewpt'->'Td' etc
    preci_df.rename(columns=
                    {'date_time': 'day', 'air_temperature_maximum': 'T_max', 'air_temperature_minimum': 'T_min',
                     'precis': 'preci', 'forecast_icon_code': 'icon',
                     'probability_of_precipitation': 'pop', 'precipitation_range': 'rainfall'}, inplace=True)

    preci_df.set_index(['location', 'day'], inplace=True)

    #with open(os.path.join(cur_dir, 'data', 'preci_file.csv'), 'wb') as f:
    #    preci_df.to_csv(f)
    # preci_df.to_csv(open(os.path.join(cur_dir, 'data', 'preci_file.csv'), 'wb') as f)

    # if fn called with request for specific preci forecast
    if myloc:
        print(myloc,avid_preci[myloc])
        return preci_df.loc[avid_preci[myloc],]
    else:
        return preci_df  # return all precis


def get_precis_old(myloc=None):
    import pandas as pd
    # import numpy as np
    # import requests
    import wget
    import os
    '''
    import re
    import json
    from bs4 import BeautifulSoup
    import xml.etree.ElementTree as etree

    from datetime import date, datetime, timedelta
    from dateutil.relativedelta import relativedelta
    '''
    '''
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    FUNCTION TO READ PRECI FORECAST FOR GIVE LOCATION
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
     Now find preci location match for given avid by looking at
     the attribute "description" for the <area> element.

     <area aac="QLD_PT038" description="Beaudesert"  type="location" parent-aac="QLD_PW015">

     There are 4 attributes, get values for attributes as a Python dictionary
     e.g item.attrib['description']  would give name of preci location
    '''

    # http://www.bom.gov.au/qld/forecasts/map7day.shtml

    def get_preci_forecasts(loc,tree):

        # get list of all <area> element tags - some 180 to 240 preci locations!!
        lists = (tree.findall("forecast/area"))

        for item in lists:
            # find matching town or location
            if (loc.lower() in item.attrib['description'].lower()):
                time = (item.findall("forecast-period"))
                time = time[0].attrib['start-time-local']

                # print ("\n\n###############################################################\n")
                # print ("Forecast for:\t {} issued at:\t {}"(format(item.attrib['description']), format(time)))
                # print ("\nForecast for ", item.attrib['description']," issued at:" , time,"\n")
                # print(item.attrib)

                fcst_param_list = []

                for day in item.iter('forecast-period'):
                    fcst_dict = {}
                    # print ("\nForecasts for day:\t\t", day.attrib['start-time-local'])
                    for item in day.findall('element'):
                        # print (item.get('type'),":\t\t", item.text)
                        fcst_dict.update({item.get('type'): item.text})

                    for item in day.findall('text'):
                        # print (item.get('type'),":\t\t", item.text)
                        fcst_dict.update({item.get('type'): item.text})

                    fcst_dict.update({'date_time': day.attrib['start-time-local']})
                    fcst_param_list.append(fcst_dict)

                # print(fcst_param_list)
                return (pd.DataFrame.from_dict(data=fcst_param_list, orient='columns'))

            else:
                # print("Preci loc not found")
                # break  # DONT - GO TO NEXT ITEM!!
                continue

    '''
    precis = ['Caloundra', 'Caboolture', 'Redcliffe', 'Nambour', 'Noosa Heads', 'Maleny', 'Maroochydore',
              'Brisbane', 'Kenmore', 'Ferny Grove', 'Oxley', 'Mount Gravatt',
              'Manly', 'Coolangatta', 'Robina', 'Nerang', 'Coomera', 'Surfers Paradise',
              'Laidley', 'Beaudesert', 'Boonah', 'Esk', 'Gatton', 'Ipswich',
              'Bundaberg', 'Maryborough', 'Hervey Bay', 'Monto', 'Gayndah', 'Gympie',
              'Dalby', 'Chinchilla', 'Miles', 'Kingaroy', 'Toowoomba', 'Warwick', 'Goondiwindi', 'Stanthorpe',
              'Gladstone', 'Rockhampton', 'Biloela', 'Yeppoon',
              'Mackay', 'Bowen', 'Carmila', 'Hamilton Island', 'Proserpine',
              'Townsville', 'Ayr', 'Ingham',
              'Cairns', 'Atherton', 'Mareeba', 'Innisfail', 'Cardwell', 'Cooktown',
              'Charters Towers', 'Georgetown', 'Hughenden', 'Richmond',
              'Normanton', 'Burketown', 'Croydon', 'Doomadgee', 'Kowanyama', 'Mornington Island',
              'Weipa', 'Aurukun', 'Coen', 'Laura', 'Lockhart River', 'Palmerville', 'Thursday Island',
              'Charleville', 'Roma', 'St George', 'Augathella', 'Bollon', 'Cunnamulla', 'Injune', 'Surat', 'Birdsville',
              'Bedourie', 'Boulia', 'Quilpie', 'Thargomindah', 'Windorah',
              'Mount Isa', 'Camooweal', 'Julia Creek', 'Urandangi', 'Cloncurry',
              'Longreach', 'Barcaldine', 'Blackall', 'Isisford', 'Tambo', 'Winton',
              'Emerald', 'Clermont', 'Moranbah', 'Blackwater', 'Dysart',
              'Rolleston', 'Springsure', 'Taroom']
    '''

    '''
    preci_url = 'http://qld-aifs-op.bom.gov.au/gfe/products/IDQ11295.xml'
    preci_response = requests.get(preci_url)

    with open('/tmp/preci_data.xml', 'wb') as f:
        f.write(preci_response.content)

    tree = etree.parse('/tmp/preci_data.xml')

    # requests module does not not works with ftp downloads
    # preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml'
    # InvalidSchema: No connection adapters were found for 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml'
    # use wget instead if not on internal bom LAN
    # wget module, which doesn't require you to open the destination file
    # just give url and filename with path
    '''

    try:
        os.remove(os.path.join(cur_dir, 'data', 'preci_file.xml'))
    except OSError:
        pass

    preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml'

    wget.download(preci_url, os.path.join(cur_dir, 'data', 'preci_file.xml'))
    with open(os.path.join(cur_dir, 'data', 'preci_file.xml'), 'r') as f:
        tree = etree.parse(f)

    preci_df_list = []

    for avid,location in avid_preci.items():
        # print('Weather forecasts for avid:{}-->{}'.format(avid,location.upper()))
        preci_df = get_preci_forecasts(location,tree) # avid_preci[location],tree)

        # convert day into datetime index object
        if preci_df is None:
            print("location is Nonetype")
        else:
            preci_df['location'] = location
            preci_df['date_time'] = \
                preci_df['date_time'].str.extract(r'(\d{4}-\d{2}-\d{2})', expand=True)
            preci_df['date_time'] = pd.to_datetime(preci_df['date_time'], errors='coerce')
            preci_df_list.append(preci_df)

    preci_df = pd.concat(preci_df_list) # ,sort=True) # Only OYTHONANYWHERE.COM
    '''
    /home/vinorda/storm_predict/utility_functions_june10.py:3767: FutureWarning: Sorting because non-concatenation axis is not aligned. A future version
    2018-07-24 10:27:44,207: of pandas will change to not sort by default.
    2018-07-24 10:27:44,207: To accept the future behavior, pass 'sort=True'.
    2018-07-24 10:27:44,208: To retain the current behavior and silence the warning, pass sort=False
    2018-07-24 10:27:44,208:   preci_df = pd.concat(preci_df_list

    2018-07-24 10:27:44,568: /home/vinorda/storm_predict/utility_functions_june10.py:3788: PerformanceWarning: indexing past lexsort depth may impact performance.
    2018-07-24 10:27:44,569:   return preci_df.loc[avid_preci[myloc],]
    2018-07-24 10:27:59,070: /home/vinorda/.local/lib/python3.6/site-packages/pandas/core/series.py:850: FutureWarning:
    2018-07-24 10:27:59,070: Passing list-likes to .loc or [] with any missing label will raise
    2018-07-24 10:27:59,070: KeyError in the future, you can use .reindex() as an alternative.
    '''

    '''Note that not all precis issues have same fields
    For e.g 4pm issue would not have rainfall amnt or pop or max and min T for current day
    4am issue has no MinT to current day etc,
    Check time of day and have different column names based on time of day
    '''

    # abbreviate some of the longer column names .e.g 'air_temp' -> 'T', 'dewpt'->'Td' etc
    preci_df.rename(columns=
                    {'date_time': 'day', 'air_temperature_maximum': 'T_max', 'air_temperature_minimum': 'T_min',
                     'precis': 'preci', 'forecast_icon_code': 'icon',
                     'probability_of_precipitation': 'pop', 'precipitation_range': 'rainfall'}, inplace=True)

    preci_df.set_index(['location', 'day'], inplace=True)

    #with open(os.path.join(cur_dir, 'data', 'preci_file.csv'), 'wb') as f:
    #    preci_df.to_csv(f)
    # preci_df.to_csv(open(os.path.join(cur_dir, 'data', 'preci_file.csv'), 'wb') as f)

    # if fn called with request for specific preci forecast
    if myloc:
        print(myloc,avid_preci[myloc])
        return preci_df.loc[avid_preci[myloc],]
    else:
        return preci_df  # return all precis


def get_precis_state(state='qld'):
    ## see http://fredgibbs.net/tutorials/extract-geocode-placenames-from-text-file
    ## https://pypi.org/project/geopy/
    ## https://stackoverflow.com/questions/48239455/indexerror-list-index-out-of-range
    import pandas as pd
    # import numpy as np
    import requests
    import wget
    import os
    import xml.etree.ElementTree as etree

    # http://www.bom.gov.au/qld/forecasts/map7day.shtml
    cur_dir = '/home/accounts/vinorda/IT_stuff/python/flask_projects/storm_predictv2'
    cur_dir = '/home/bou/stats-R/flask_projects/storm_predictv3'

    '''geolocate placenames (get latitude and longitude coordinates).
    send requests to the Google Geocoding API and
    process the JSON response that it returns.
    # api-endpoint '''
    url = 'http://maps.googleapis.com/maps/api/geocode/json'

    '''Usage
    r = requests.get(URL, params=DICTIONARY)
    the API expects us to send two bits of information:
    address (in this case our place name), and
    sensor (which the API requires to be set to true or false).
    '''

    if state == 'qld':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml'
    elif state == 'nsw':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDN11060.xml'
    elif state == 'nt':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDD10207.xml'
    elif state == 'sa':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDS10044.xml'
    elif state == 'vic':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10753.xml'
    elif state == 'wa':
        preci_url = 'ftp://ftp.bom.gov.au/anon/gen/fwo/IDW14199.xml'
    elif state == None:
        # get all states
        # wud need another outer loop
        # for state in ['nsw','qld',......]:
        pass

    try:
        # remove previous XML file
        os.remove(os.path.join(cur_dir, 'data', state + '_preci_file.xml'))
    except OSError:
        pass

    wget.download(preci_url, os.path.join(cur_dir, 'data', state + '_preci_file.xml'))

    # os.sleep(5)

    with open(os.path.join(cur_dir, 'data', state + '_preci_file.xml'), 'r') as f:
        tree = etree.parse(f)

    # get list of all <area> element tags - some 180 to 240 preci locations!!
    lists = tree.findall("forecast/area")
    print('Number of forecast/areas in ', state, " = ", len(lists))
    precis_list = []
    location = None
    state_xml = None

    for item in lists:
        # print('item',item)
        if (item.attrib['type'] == 'region'):
            state_xml = item.attrib['description']
            continue
        if (item.attrib['type'] == 'public-district'):
            # district = item.attrib['description']
            continue

        # find matching town or location
        location = item.attrib['description']
        print('Processing preci location', location)

        # Defining a params dict for the parameters to be sent to the API
        payload = {'address': str(location + ',' + state_xml + ',Australia'), 'sensor': 'false'}

        # print ('Geolocating:', payload['address'])
        # Sending get request and saving the response as response object
        # Make sure that you had a successful request
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            # Extracting data in json format
            data = r.json()

            '''an empty array (data['results']) will raise the exception
            IndexError : List index Out of range
            also make sure that the field results exists in the dictionary data.
            Otherwise the call to data["results"] will raise a
            KeyError exception... Try dict.get(key) instead of dict[key]'''

            if data.get("results", []):
                # Extracting latitude, longitude and formatted address
                # of the first matching location
                # print(data['results'][0]['geometry']['location'])
                lat = data['results'][0]['geometry']['location']['lat']
                lon = data['results'][0]['geometry']['location']['lng']
                # formatted_address = data['results'][0]['formatted_address']

                # Printing the output
                # print("Latitude:%s\nLongitude:%s\nFormatted Address:%s"
                #       %(lat, lon,formatted_address))

        # time = item.findall("forecast-period")
        # print('time',time)
        # time = time[0].attrib['start-time-local']

        # print ("\n\n###############################################################\n")
        # print ("Forecast for:\t {} issued at:\t {}".format(item.attrib['description'], format(time)))
        # print(item.attrib)

        # for each day - get preci day/date,and actual preci (max,min,icon etc)
        days = []
        for day in item.iter('forecast-period'):
            fcst_dict = {}
            # print ("\nForecasts for day:\t\t", day.attrib['start-time-local'])
            for item in day.findall('element'):
                # print (item.get('type'),":\t\t", item.text)
                fcst_dict[item.get('type')] = item.text
                # fcst_dict.update({item.get('type'): item.text})

            for item in day.findall('text'):
                # print (item.get('type'),":\t\t", item.text)
                fcst_dict[item.get('type')] = item.text
                # fcst_dict.update({item.get('type'): item.text})

            # fcst_dict.update({'location': location})
            fcst_dict['location'] = location
            fcst_dict['state'] = state
            fcst_dict['lat'] = lat
            fcst_dict['lon'] = lon
            # fcst_dict.update({'date_time': day.attrib['start-time-local']})
            fcst_dict['date_time'] = day.attrib['start-time-local']

            # print(fcst_dict.items())
            # print(fcst_dict.keys())
            # print(fcst_dict.values())
            days.append(fcst_dict)

        dat = pd.DataFrame.from_dict(data=days, orient='columns')
        dat['date_time'] = \
            dat['date_time'].str.extract(r'(\d{4}-\d{2}-\d{2})', expand=True)
        dat['date_time'] = pd.to_datetime(dat['date_time'], errors='coerce')
        # print(dat)
        precis_list.append(dat)

    preci_df = pd.concat(precis_list)

    # df[df.location.str.contains('Boonah')]  will give us Boonah precis only
    # abbreviate some of the longer column names .e.g 'air_temp' -> 'T', 'dewpt'->'Td' etc
    preci_df.rename(columns=
                    {'date_time': 'day', 'air_temperature_maximum': 'T_max',
                     'air_temperature_minimum': 'T_min', 'precis': 'preci',
                     'forecast_icon_code': 'icon', 'probability_of_precipitation': 'pop',
                     'precipitation_range': 'rainfall'}, inplace=True)

    '''Note that not all precis issues have same fields
    For e.g 4pm issue would not have rainfall amnt or pop or max and min T for current day
    4am issue has no MinT to current day etc,
    Check time of day and have different column names based on time of day

    preci_df.set_index(['location', 'day'], inplace=True)

    with open(os.path.join(cur_dir, 'data', state+'_preci_file.csv'), 'wb') as f:
        preci_df.to_csv(f)
    preci_df.to_csv(open(os.path.join(cur_dir, 'data', state+'_preci_file.csv'), 'wb') as f)

    # if fn called with request for specific preci forecast
    if myloc:
        print(myloc,avid_preci[myloc])
        return preci_df.loc[avid_preci[myloc],]
    else:
        return preci_df  # return all precis   '''

    # force numeric col values
    for col in ['lat', 'lon', 'T_max', 'T_min']:
        preci_df[col] = pd.to_numeric(preci_df[col], errors='coerce')

    # with open(os.path.join(cur_dir, 'data', state+'_preci_file.csv'), 'wb') as f:
    #    preci_df.to_csv(f)

    if (len(preci_df.columns)) == 11: # extra col wud be rainfall !!
        preci_df = preci_df[['location', 'state', 'lat', 'lon', 'day', 'icon', \
                             'T_max', 'T_min', 'pop', 'preci', 'rainfall']]
    elif (len(preci_df.columns)) == 10:
        preci_df = preci_df[['location', 'state', 'lat', 'lon', 'day', 'icon', \
                             'T_max', 'T_min', 'pop', 'preci']]

    preci_df.to_csv(cur_dir + '/data/' + state + '_preci_file.csv', sep=',', header=True)

    return (preci_df)


# Fn below is for creating sfc wind climatology based on
# get days with similar gradient wind to Brisbane Sonde
def get_matching_days(grad_wnd_dir, grad_wnd_spd, SLP, sonde):
#def get_matching_days(grad_wnd_dir, grad_wnd_spd, sonde):
    if (grad_wnd_dir >= 16) & (grad_wnd_dir <= 344):
        UDL = grad_wnd_dir - 15
        UDR = grad_wnd_dir + 15
        print("(grad_wnd_dir >= 16) & (grad_wnd_dir <= 344)", UDL, UDR)
        grad_dir_mask = \
            (sonde['wdir900'] >= UDL) & \
            (sonde['wdir900'] <= UDR)

    elif (grad_wnd_dir >= 345) & (grad_wnd_dir <= 360):
        UDL = grad_wnd_dir - 15
        UDR = grad_wnd_dir + 15 - 360
        print("(grad_wnd_dir >= 16) & (grad_wnd_dir <= 344)", UDL, UDR)
        grad_dir_mask = \
            (sonde['wdir900'] >= UDL) | \
            (sonde['wdir900'] <= UDR)

    elif (grad_wnd_dir >= 0) & (grad_wnd_dir <= 15):
        UDL = grad_wnd_dir - 15 + 360
        UDR = grad_wnd_dir + 15
        print("(grad_wnd_dir >= 16) & (grad_wnd_dir <= 344)", UDL, UDR)
        grad_dir_mask = \
            (sonde['wdir900'] >= UDL) | \
            (sonde['wdir900'] <= UDR)
    else:
        print("No shit wind", sonde['wdir900'])

    USL = grad_wnd_spd - 5
    USR = grad_wnd_spd + 5
    grad_spd_mask = (sonde['wspd900'] > USL) & \
                    (sonde['wspd900'] < USR)

    SPL = SLP - 5
    SPR = SLP + 5
    qnh_mask = (sonde['P'] > SPL) &  (sonde['P'] < SPR)

    mask = grad_dir_mask & grad_spd_mask & qnh_mask

    try:
        match_days = sonde.loc[mask].index
    except:
        print("No matching synoptic days found in dataset")
        # exit - calling fn expected to deal with situation

    return match_days



'''
Haversine (or Great Circle) distance formula.
https://en.wikipedia.org/wiki/Haversine_formula
Copyright
https://github.com/sversh/pycon2017-optimizing-pandas
https://www.youtube.com/watch?v=HN5d490_KKk
https://www.superherosupplies.com/

function takes the latitude and longitude of two points,
adjusts for Earth’s curvature,
and calculates the straight-line distance between them

Usage: say to find dist between given point and all other
data points in a dataframe df

df['distance'] = df.apply(lambda row:
    haversine(40.671, -73.985, row['latitude'], row['longitude']), axis=1)

# Vectorized implementation of Haversine applied on Pandas series
df['distance'] = haversine(40.671, -73.985, df['latitude'], df['longitude'])


50-fold improvement over the apply() method,
and more than a 100-fold improvement over iterrows() by
vectorizing the function — 
didn’t need to do anything but change the input type tp pandas Series!
'''
'''
# Define a basic Haversine distance formula
def haversine(lat1, lon1, lat2, lon2):
    MILES = 3959 # 6367 km is the radius of the Earth
    # convert decimal degrees to radian
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    total_miles = MILES * c
    return total_miles
'''

def haversine(lon1, lat1, lon2, lat2):

    from math import radians, cos, sin, asin, sqrt, atan2
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    #c = 2 * asin(sqrt(a))
    c = 2 * atan2(sqrt(a),sqrt(1-a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return(km)