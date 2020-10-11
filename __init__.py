"""
Created on Thu Apr 26 13:24:40 2018
@author: bou
Python application using Flask web framework.
Application calculates storm potential based on historical station sonde dataset

HELP YOU

https://www.medcalc.org/manual/roc-curves.php
sonde data
http://slash.dotat.org/atmos/help.html

http://flask.pocoo.org/
https://www.w3schools.com/
http://stackabuse.com/serving-static-files-with-flask/
https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Your_first_HTML_form
http://www.3plearning.com/tech/flash/#browsers


http://slash.dotat.org/cgi-bin/atmos
https://galaxydatatech.com/2018/04/01/visualizations-database-data/
http://rwet.decontextualize.com/book/web-applications/
http://flask.pocoo.org/docs/1.0/patterns/fileuploads/

These 3 very good flas tutorials...
https://overiq.com/flask/0.12/sessions-in-flask/
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins

####  Creating Web APIs with Python and Flask ####
https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
#### Simple Web Applications with Flask  ####
http://www.compjour.org/lessons/flask-single-page/
## Creating Charts with Chart.js in a Flask Application ##
https://www.patricksoftwareblog.com/creating-charts-with-chart-js-in-a-flask-application/

https://www.blog.pythonlibrary.org/2017/12/12/flask-101-adding-a-database/
https://blog.pythonanywhere.com/
https://www.webforefront.com/django/usebuiltinjinjastatements.html

Plotting
https://galaxydatatech.com/2018/04/01/passing-plots-web-page/
https://www.datacamp.com/courses/visualizing-time-series-data-in-python
https://www.coursera.org/learn/python-plotting
http://www.aosabook.org/en/matplotlib.html

Security
https://fedoramagazine.org/secure-your-webserver-improved-certbot/
Certbot fully compatible with Python 3


"""

from flask import Flask, url_for, render_template, request, redirect
from flask import make_response,flash,session, abort
from flask_script import Manager, Command, Shell
# from form import forms
from forms import Sonde_updateForm, gpats_inputForm, webcam_inputForm
import datetime


# plotting libraries
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#plt.style.use('ggplot')

from io import BytesIO
'''
https://webkul.com/blog/using-io-for-creating-file-object/
https://www.journaldev.com/19178/python-io-bytesio-stringio
https://www.programcreek.com/python/example/1734/io.BytesIO
'''


import csv
import os
import re
import math
import pickle
#import sqlite3
import pandas as pd
import numpy as np
import importlib
import utility_functions_sep2018 as bous
# from tabulate import tabulate
# from avlocs import get_avlocs
import logging
logger = logging.getLogger('aero_intel')

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

cur_dir = os.path.dirname(__file__)

# creates a Flask application, named app
app = Flask(__name__)# instantiate an object of class Flask

# to start the debugger and reloader -
# set debug attribute of the application instance (app) to True
# app.debug = True  <- already done inside if __name__ == "__main__":
'''
from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="vinorda",
    password="shobysbou",
    hostname="vinorda.mysql.pythonanywhere-services.com",
    databasename="vinorda$comments",
)


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
'''


app.config['SECRET_KEY'] = 'a very bad password'
app.permanent_session_lifetime = datetime.timedelta(days=1)#0.0005)
# don't set to 0 - then won't remember sonde data and predictions fail
# with no obvious reasons why --- DONT MAKE

# app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
manager = Manager(app)

# get precis for all locations when program starts
# global varible accessible by all modules
precis = bous.get_precis()

'''
23:24 ~/storm_predict (master)$ ipython3.6
Python 3.6.0 (default, Jan 13 2017, 00:00:00)
IPython 4.1.2 -- An enhanced Interactive Python.
In [1]: from flask_app import db
In [2]: db.create_all()
In [3]: db
Out[3]: <SQLAlchemy engine=mysql+mysqlconnector://vinorda:***@vinorda.mysql.pythonanywhere-services.com/vinorda$comments?charset=utf8>

mysql> show tables;
+----------------------------+
| Tables_in_vinorda$comments |
+----------------------------+
| comments                   |
+----------------------------+


mysql> describe comments;
+---------+---------------+------+-----+---------+----------------+
| Field   | Type          | Null | Key | Default | Extra          |
+---------+---------------+------+-----+---------+----------------+
| id      | int(11)       | NO   | PRI | NULL    | auto_increment |
| content | varchar(4096) | YES  |     | NULL    |                |
+---------+---------------+------+-----+---------+----------------+

'''


######## Flask (Web stuff) #########################################
'''Application error handlers.
https://opensource.com/article/17/3/python-flask-exceptions
'''
from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(Exception)
def handle_error(error):
    message = [str(x) for x in error.args]
    status_code = error.status_code
    success = False
    response = {
        'success': success,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }
    return jsonify(response), status_code

import requests
def is_url_ok(url):
    return 200 == requests.head(url).status_code


def get_airport_csv():
    airports = bous.get_avlocs().reset_index()
    print(airports.head())
    print("isnull().any()", airports.isnull().any())
    airports = airports.to_dict(orient='records')
    print("Airports shape after drop na", len(airports))  #dict has no shape
    return airports

# list all the available API paths defined for the application. Using the response given by this method on the client-side, we could build up a dynamic client for it. It's a best practice to have a route, which displays all the paths configured inside an application

@app.route("/api", methods=["GET"])
def list_routes():
	result = []
	for rt in app.url_map.iter_rules():
		result.append({
			"methods": list(rt.methods),
			"route": str(rt)
		})
	return jsonify({"routes": result, "total": len(result)})


# root '/' and index both both to our home page
@app.route('/', methods=["GET"])
@app.route('/index/', methods=["GET"])
@app.route('/aussy_airports/', methods=["GET"])
def index():
    # update - get new precis every time we go home page
    # precis = bous.get_precis()
    # template = "airports.html"  # html page to render
    airports = get_airport_csv()     # get airport data as a dict obj
    print (airports[:1])     # list of dict entries - each dict is one row from df
    # print("Render time!!!!")
    return render_template("aussie_airports.html", object_list=airports)

@app.route('/post_update/', methods=['get', 'post'])
def post_update():

    day = pd.datetime.today().strftime('%Y-%m-%d')
    stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']
    area = 'SE QLD'

    if (request.method == "POST"): # & ("post-feedback-form" in request.form):
        comment = Comment(content=request.form["contents"])
        flash("Comments posted", comment)
        db.session.add(comment)
        db.session.commit()

        #return redirect(url_for('index'),comments=Comment.query.all() )
        return render_template('thunderstorm_predict.html',day=day, stations=stations,
                            area=area,show_obs='show' ) #,comments=Comment.query.all())


'''
When user clicks Thunderstorm Climatology on base page 

<tr><td><a href={{ url_for('gpats') }}>Thunderstorm Climatology</a></td></tr>

renders render_template('gpats.html'  from templates folder
but url route is http://qld-rfc-ws45/gpats_climatology/
'''

@app.route('/gpats_climatology/', methods=["GET", "POST"])
def gpats():

    from flask import Markup
    stations = bous.area40
    # stations = stations.append(bous.area41)
    '''wrap string in a Markup object before passing it to the template
    also in base.html use safe filter so we render html not text {{ mesagesafe}} '''

    message = Markup('<p>GPATS climatology boxplots and heatmaps produced early 2017 \
    - so bit old but still relevant - will update soon with latest data!!!\
    see <a href="/static/docs/GpatsBasedStationThunderstormClimatology_Documentation.html">documentation</a>')
    #see <a href="/static/docs/GpatsBasedStationThunderstormClimatology_Documentation.docx">documentation</a>')

    flash(message)
    '''we have some older static heatmaps here for display only
    to create new ones go to gpats_heatmaps '''
    hours = range(0,12,1)
    return render_template('gpats.html', stations=stations,hours=hours)




'''
When user clicks FOG Climatology on base page 
<tr><td><a href={{ url_for('fog') }}>FOG Climatology</a></td></tr>
renders render_template('fog_climatology.html' from templates folder
but url route is http://qld-rfc-ws45/fog_stuff/
'''

@app.route('/fog_stuff/', methods=["GET", "POST"])
def fog():
    stations = ['YBBN', 'YBSU','YBTL','YSCB', 'YSSY','YMML','YPAD']
    flash("These Fog climatology plots were produced Dec 2015 - so bit old and dusty.")
    #return redirect(url_for('index'))
    return render_template('fog_climatology.html', stations=stations)




'''
Renders this page with form to collect user sonde data 

http://qld-rfc-ws45/sonde_update/

Once it saves sonde data to a global variable reutns user to index page 

return redirect(url_for('index')) ---> http://qld-rfc-ws45/aussy_airports/
'''


@app.route('/sonde_update/', methods=['get', 'post'])
def sonde_update():
    day = pd.datetime.today().strftime('%Y-%m-%d')
    print("sonde_update() called")
    form = Sonde_updateForm()
    if form.validate_on_submit():
        print("sonde_update() called - form validated on post")
        st_name = form.st_name.data
        sonde_time = form.sonde_time.data
        t850 = float(form.t850.data)
        t500 = float(form.t500.data)
        tmp_rate850_500 = float(t850 - t500)
        wnd900 = form.wnd900.data
        wdir_900,wspd_900 = wnd900.split("/")
        wnd500 = form.wnd500.data
        wdir_500,wspd_500 = wnd500.split("/")
        QNH = float(form.QNH.data)

        sonde_item = {'sonde_station': st_name, 'sonde_time': sonde_time,
            't850': t850, 't500': t500,
            'wdir900': wdir_900, 'wspd900': wspd_900,
            'wdir500': wdir_500, 'wspd500': wspd_500,
            'tmp_rate850_500': tmp_rate850_500, 'P': QNH}

        # sonde_data = pd.Series(sonde_item)  # whats da point in doin tis?

        print(sonde_item,sep='')
        session['sonde_item'] = sonde_item
        session.modified = True

        print(st_name,sonde_time, t850, t500,wnd900, wnd500, QNH)
        flash(session['sonde_item'])
    else:
        return render_template('sonde_update.html', form=form)
    return redirect(url_for('storm_predict'))

'''
   st_name = RadioField('Sonde station',
                        choices = [('YBBN','Brisbane'),('YBRK','Rockhampton')],
                        [validators.Required("Please enter sonde station.")])

   sonde_time = SelectField('Sonde Time',
                        choices = [('05Z', '3PM Afternoon Sonde'),
                                   ('23Z', '9AM Mid Morning Sonde')],
                        [validators.Required("Please enter sonde station.")])

   t850 = DecimalField("850hPa Temperature",\
                       [validators.Required("Please enter 850 temp.")])
   t500 = DecimalField("500hPa Temperature",\
                       [validators.Required("Please enter 500 temp.")])
   wnd500 = TextField("500hPa winds e.g 340/20",\
                       [validators.Required("Please enter 500 winds.")])


Why we are using validate_on_submit() instead of validate() as in the console ?

The validate() method simply checks whether the form data is valid or not,
it doesn't check whether the request is submitted using the POST method or not.
That means if use we validate() method then a GET request to /contact/ would
trigger the form validation and users will see validation errors in the form.
In general, we trigger validation routines only when the data is submitted
using the POST request. The validate_on_submit() method returns True when
the form is submitted using the POST request and data is valid.
Otherwise False. The validate_on_submit() method internally calls the
validate() method.

Also, notice that we are not passing any data while
instantiating the form object because when the form is submitted using the
POST request WTForms reads the form data from the request.form attribute.

The form fields defined in the form class becomes attribute to the form object.
To access field data we use the data attribute of the form field:

form.name.data   # access the data in the name field.
form.email.data   # access the data in the email field.

To access all the form data at once use the data attribute of the form object:

form.data   # access all the form data

When you visit URL /contact/ using the GET request,
the validate_on_submit() method returns False, the code inside the if body is
skipped and the user is displayed an empty HTML form.

When the form is submitted using the POST request, the validate_on_submit()
returns True assuming the data is valid. The print() calls inside the if body
prints the data entered by the user and the redirect() function redirects
the user to the /contact/ page.

On the other hand if validate_on_submit() returns False execution of statements
inside the if body is skipped and form with validation errors is displayed
'''


@app.route('/session/')
def updating_session():
    res = str(session.items())

    sonde_item = {'sonde_station': 'YBBN', 'sonde_time': '23Z'}

    if 'sonde_item' in session:
        session['sonde_item']['sonde_station'] = 'YBBN'
        session.modified = True
    else:
        session['sonde_item'] = sonde_item

    return res

'''
https://overiq.com/flask/0.12/creating-urls-in-flask/

To generate URLs for dynamic routes pass dynamic parts as keyword arguments
with app.test_request_context('/api'):
...    url_for('user_profile', user_id = 100)

'/user/100/'

 with app.test_request_context('/api'):
...    url_for('books', genre='biography')

'/books/biography/'

The extra number of keywords arguments passed to the url_for()
function will be appended to the URL as a query string.

with app.test_request_context('/api'):
...    url_for('books', genre='biography', page=2, sort_by='date-published')
...
'/books/biography/?page=2&sort_by=date-published'

The url_for() is available to you inside the template.
To generate URLs inside templates simply call url_for() inside the
double curly braces {{ ... }}, as follows:

<a href="{{ url_for('books', genre='biography') }}">Books</a>

Output:
<a href="/books/biography/">Books</a>

Flask automatically adds a route of the form /static/<filename> to handle
static files. So all we need to serve static files is to create
URLs using the url_for() function as follows:

<script src="{{ url_for('static', filename='jquery.js') }}"></script>
Output:
<script src="/static/jquery.js"></script>

'''

@app.route('/plot_obs_time_series/<string:sta>/', methods=['GET'])
def plot_obs_time_series(sta):

    print("Calling plot_obs_time_series() to plot T and TD time series with {}".format(sta))

    from io import BytesIO
    # from flask import send_file
    # send_file throws "<built-in function uwsgi_sendfile> returned a result with an error set"
    # use Response instead
    from flask import Response
    # from werkzeug import FileWrapper
    # see https://www.pythonanywhere.com/forums/topic/13570/
    from werkzeug.wsgi import FileWrapper

    import datetime as dt
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    # convert compass direction to corresponding degrees
    # see http://codegolf.stackexchange.com/questions/54755/convert-a-point-of-the-compass-to-degrees
    def f(s):
        if 'W' in s:
            s = s.replace('N', 'n')
        a = (len(s) - 2) / 8
        if 'b' in s:
            a = 1 / 8 if len(s) == 3 else 1 / 4
            return (1 - a) * f(s[:-2]) + a * f(s[-1])
        else:
            if len(s) == 1:
                return 'NESWn'.find(s) * 90
            else:
                return (f(s[0]) + f(s[1:])) / 2

    # Make meteogram plot
    class Meteogram(object):
        """ Plot a time series of meteorological data from a particular station as a
        meteogram with standard variables to visualize, including thermodynamic,
        kinematic, and pressure. The functions below control the plotting of each
        variable.
        TO DO: Make the subplot creation dynamic so the number of rows is not
        static as it is currently. """

        def __init__(self, fig, dates, station, time=None, axis=0):
            """
            Required input:
                fig: figure object
                dates: array of dates corresponding to the data
                probeid: ID of the station
            Optional Input:
                time: Time the data is to be plotted
                axis: number that controls the new axis to be plotted (FOR FUTURE)
            """
            if not time:
                time = dt.datetime.utcnow()
            self.start = dates[0]
            self.fig = fig
            self.end = dates[-1]
            self.axis_num = 0
            self.dates = mpl.dates.date2num(dates)
            self.time = time.strftime('%Y-%m-%d %H:%M UTC')
            self.title = 'Latest Ob Time: {0}\nProbe ID: {1}'.format(self.time, station)

        def plot_winds(self, ws, wd, wsmax, plot_range=None):
            """
            Required input:
                ws: Wind speeds (knots)
                wd: Wind direction (degrees)
                wsmax: Wind gust (knots)
            Optional Input:
                plot_range: Data range for making figure (list of (min,max,step))
            """
            # PLOT WIND SPEED AND WIND DIRECTION
            self.ax1 = fig.add_subplot(4, 1, 1)  # (4,1,1) - 4 rows, 1 col, tis is 1st row

            # plots dates vs wind speed - line plot and fill
            ln1 = self.ax1.plot(self.dates, ws, label='Wind Speed')
            # self.ax1.fill_between(self.dates, ws, 0) # x axis 1st date to last date value
            self.ax1.set_xlim(self.start, self.end)
            if not plot_range:
                plot_range = [-1, np.max(wsmax)+1, 1]
            self.ax1.set_ylabel('Wind Speed (knots)', multialignment='center')
            self.ax1.set_ylim(plot_range[0], plot_range[1], plot_range[2])
            self.ax1.grid(b=True, which='major', axis='y', color='k', linestyle='--',
                          linewidth=0.5)
            # ln2 = self.ax1.plot(self.dates, wsmax, '.b', label='1-min Wind Gust (knots)')  # plot blue dots
            ln2 = self.ax1.plot(self.dates, wsmax, label='1-min Wind Gust (knots)')          # plot blue lines

            ax7 = self.ax1.twinx()
            ln3 = ax7.plot(self.dates, wd, '.k', linewidth=0.5, label='Wind Direction')
            ax7.set_ylabel('Wind\nDirection\n(degrees)', multialignment='center')
            ax7.set_ylim(0, 360)
            ax7.set_yticks(np.arange(start=30, stop=360, step=30)) # , ['NE', 'SE', 'SW', 'NW'])
            lns = ln1 + ln2 + ln3
            labs = [l.get_label() for l in lns]
            ax7.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
            ax7.legend(lns, labs, loc='upper center',
                       bbox_to_anchor=(0.5, 1.2), ncol=3, prop={'size': 12})

        def plot_thermo(self, t, td, plot_range=None):
            """
            Required input:
                T: Temperature (deg F)
                TD: Dewpoint (deg F)
            Optional Input:
                plot_range: Data range for making figure (list of (min,max,step))
            """
            # PLOT TEMPERATURE AND DEWPOINT
            if not plot_range:
                plot_range = [np.min(td)-1, np.max(t)+1, 2]
            self.ax2 = fig.add_subplot(4, 1, 2, sharex=self.ax1)  #(4,1,2) - 4 rows, 1 col, tis is 2nd plot
            ln4 = self.ax2.plot(self.dates, t, 'r-', label='Temperature')
            self.ax2.fill_between(self.dates, t, td, color='r',alpha=0.1) # DONT FILL

            self.ax2.set_ylabel('Temperature\n(C)', multialignment='center')
            self.ax2.grid(b=True, which='major', axis='y', color='k', linestyle='--',
                          linewidth=0.5)
            self.ax2.set_ylim(plot_range[0], plot_range[1], plot_range[2])

            ln5 = self.ax2.plot(self.dates, td, 'g-', label='Dewpoint')
            #self.ax2.fill_between(self.dates, td, self.ax2.get_ylim()[0], color='g') # DONT FILL

            ax_twin = self.ax2.twinx()
            ax_twin.set_ylim(plot_range[0], plot_range[1], plot_range[2])
            lns = ln4 + ln5
            labs = [l.get_label() for l in lns]
            ax_twin.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))

            self.ax2.legend(lns, labs, loc='upper center',
                            bbox_to_anchor=(0.5, 1.2), ncol=2, prop={'size': 12})


        def plot_rh(self, rh, plot_range=None):
            """
            Required input:
                RH: Relative humidity (%)
            Optional Input:
                plot_range: Data range for making figure (list of (min,max,step))
            """
            # PLOT RELATIVE HUMIDITY
            if not plot_range:
                plot_range = [0, 100, 4]
            self.ax3 = fig.add_subplot(4, 1, 3, sharex=self.ax1) #(4,1,3) - 4 rows, 1 col, tis is 3rd row
            self.ax3.plot(self.dates, rh, 'g-', label='Relative Humidity')
            self.ax3.legend(loc='upper center', bbox_to_anchor=(0.5, 1.22), prop={'size': 12})
            self.ax3.grid(b=True, which='major', axis='y', color='k', linestyle='--',
                          linewidth=0.5)
            self.ax3.set_ylim(plot_range[0], plot_range[1], plot_range[2])

            #self.ax3.fill_between(self.dates, rh, self.ax3.get_ylim()[0], color='g')
            self.ax3.set_ylabel('Relative Humidity\n(%)', multialignment='center')
            self.ax3.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
            axtwin = self.ax3.twinx()
            axtwin.set_ylim(plot_range[0], plot_range[1], plot_range[2])

        def plot_pressure(self, p, plot_range=None):
            """
            Required input:
                P: Mean Sea Level Pressure (hPa)
            Optional Input:
                plot_range: Data range for making figure (list of (min,max,step))
            """
            # PLOT PRESSURE
            if not plot_range:
                plot_range = [np.min(p)-1, np.max(p)+1, 2]
            self.ax4 = fig.add_subplot(4, 1, 4, sharex=self.ax1)  # (4,1,4) - 4 rows, 1 col, tis is 4th row/plot
            self.ax4.plot(self.dates, p, 'm', label='Mean Sea Level Pressure')
            self.ax4.set_ylabel('Mean Sea\nLevel Pressure\n(hPa)', multialignment='center')
            self.ax4.set_ylim(plot_range[0], plot_range[1], plot_range[2])

            axtwin = self.ax4.twinx()
            axtwin.set_ylim(plot_range[0], plot_range[1], plot_range[2])
            #axtwin.fill_between(self.dates, p, axtwin.get_ylim()[0], color='m')
            axtwin.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))

            self.ax4.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), prop={'size': 12})
            self.ax4.grid(b=True, which='major', axis='y', color='k', linestyle='--',
                          linewidth=0.5)

    '''  No point as we create and display plots on the fly - no need to save to disk
    try:
        #os.remove(os.path.join(cur_dir, 'static/images/plots', 'TimeSeries_{}.png'.format(sta)))
        os.remove(os.path.join('static/images/plots', 'TimeSeries_{}.png'.format(sta)))
    except OSError:
        pass
    '''

    data = bous.get_wx_obs_www([sta], hist='Yes')
    data['wdir'] = data['wdir'].apply(f)   # convert directions text like SSE to decimal
    # data.sort_index(axis=0, ascending=True, inplace=True)

    fig = plt.figure(figsize=(10, 15))  #10,8
    meteogram = Meteogram(fig, list(data.index), sta)
    meteogram.plot_winds(data['wspd'], data['wdir'], data['gust'])
    meteogram.plot_thermo(data['T'], data['Td'])
    meteogram.plot_rh(data['RH'])
    meteogram.plot_pressure(data['P'])
    fig.subplots_adjust(hspace=0.4)

    # Using nginx as uWSGI server means assets like static etc same level as app folder
    # fig.savefig(os.path.join(cur_dir, 'static/images/plots', 'TimeSeries_{}.png'.format(sta)))
    # fig.savefig(os.path.join('static/images/plots', 'TimeSeries_{}.png'.format(sta)))
    # flask can serve plot to web without having to save it to disk

    # print( "Current directory from plot_obs_time_series is", cur_dir, " and pwd is ", os.getcwd())
    print( "Current directory from get_avlocs() in utility_fucntions_sept2018 is", os.getcwd())

    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    w = FileWrapper(img)
    #return send_file(img, mimetype='image/png')
    return Response(w, mimetype='image/png', direct_passthrough=True)


'''
Function to grab TAF/ last 2 METARS from external bom page
When call this function from view fn intel(), we usually wud 
request TAF for a single station; in this instance we just return 
the TAF content to intel() view displays this TAF on the TAF intel page 

If this view function is called from the html template
<a href="{{ url_for('get_tafs',area='area40')}}">Area 40</a> Tafs
then we have many TAFS to display and show these view another TAF display page.
'''

'''
API to grab TAFORs
TAF API UASGE 
1.  Grab single TAF
http://127.0.0.1:5000/api/v1/resources/tafors?taf_id=ybbn
2. Grab Multiple TAFS
http://127.0.0.1:5000/api/v1/resources/tafors?taf_id=ybbn+yssy+ypdn+nffn
3. TAFS for given AREA Code
http://127.0.0.1:5000/api/v1/resources/tafors?area=20
4. TAFS for given State
http://127.0.0.1:5000/api/v1/resources/tafors?state=qld
5. TAFS for given Country
http://127.0.0.1:5000/api/v1/resources/tafors?cntry=fj
'''

@app.route('/api/v1/resources/tafors', methods=['GET'])
def tafors():

    import requests
    from bs4 import BeautifulSoup

    query_parameters = request.args
    sta = query_parameters.get('taf_id')
    area = query_parameters.get('area')
    state = query_parameters.get('state')
    cntry = query_parameters.get('cntry')

    '''http://ourairports.com/countries/AU/VIC/airports.html
    open calc - copy "ident" col to txt file find replace \n with ','   '''

    fijian_tafs = ['NFFN','NFNA','NFNS','NFNL','NFMA','NFNM','NFCS','NFRS','NFNB','NFCI','NFNO','NFNK','NFFO','NFMO',
    'NFNG','NFNR','NFVB','NFKD','NFKB','NFNH','NFOL','NFNV','NFVL','NFNW','NFSW','NFFA','NFNU','NTA','NFUL','NFFR','NFBG']

    # get current TAF and METARS for these stations
    stations = ''

    # get aviation location info from pca and minimz database
    locs = bous.get_avlocs()

    if 'taf_id' in request.args:
    	sta = str(request.args['taf_id'])
    	if sta in locs.index.dropna().tolist()+fijian_tafs:
    	    stations+=sta+'+'
    	if sta == 'YTTI':  # we need stuff for Truscott TAF - no longer Troughton Is TAF
    	    sta = 'YTST'
    	else:
    		return ("<h1>Sorry to dissappoint. This beta version TAF API only for Aust and Fiji!</h1>")
    elif 'area' in request.args:
        area = str(request.args['area'])
        if area in locs['AREA'].unique().tolist():
        	print("Requested area is State of :",area)
        	sta_list = locs.loc[locs['AREA'].str.contains(area)].index.tolist()
        	for sta in sta_list:
        		stations+=sta+'+'
        	print("stations in state of {}: {}".format(area, stations))
        else:
            return ("<h1>Error: No such ARFOR area in Australia, Please area like 40, 20, 80 etc.</h1>")
    elif 'state' in request.args:
        state = str(request.args['state']).upper()
        # area is name of state - str e.g "QLD"
        if state in locs['State'].unique().tolist():
        	print("Requested area is State of :",state)
        	sta_list = locs.loc[locs['State'].str.contains(state)].index.tolist()
        	for sta in sta_list:
        		stations+=sta+'+'
        	print("stations in state of {}: {}".format(state, stations))
        else:
            return ("<h1>Error: No such state in Australia, Please state like VIC, QLD, TAS etc.</h1>")
    elif 'cntry' in request.args:
    	cntry = str(request.args['cntry']).upper()
    	if cntry == 'AU':
    	    sta_list = locs.index.dropna().tolist()
    	    print(sta_list)
    	    for sta in sta_list:
    	    	stations+=sta+'+'
    	elif cntry == 'FJ':
    		for sta in fijian_tafs:
    			stations+=sta+'+'
    	else:
    		return ("<h1>Sorry to dissappoint. This beta version TAF API only for Aust and Fiji!</h1>")
    else:
    	return ("<h1>Error: No valid parameters provided. Check TAF API and try again.</h1>")

    ''' OLD CODE
    #we pass in both strings such as states like 'VIC', 'nsw', 'fj', 'au'
    #also area (an integer) such as 40, 80, 20 etc [Ensure its string b4 strip !!]
    #also try to covert to int 1st in case its an area like 40
    #WE HAVE HANDLED THIS MESSY SITUATION USING query parameters above
    try:
        area = int(area)
        print('{} can be converted to an int - so it must be be ARFOR code'.format(area))
    except ValueError as verr:
        print('{} cannot be converted to an int.\n{} must be real STRING!!'.format(area, verr))
        if isinstance(area, str):  # check again to ensure - maybe not needed !!!
            print("area requested", area)
            area = area.strip().upper()
            # area can be 2 or 3 chars long, if 4 means its a TAF location
            if len(area)==4: # Must have asked for single TAF only like 'YBBN'
                stations=area
        pass # do job to handle: s does not contain anything convertible to int
    '''


    print("Calling get_tafs() for {}, \nstations {}".format(area,stations))

    url = 'http://reg.bom.gov.au/cgi-bin/reg/dmsu/get_tafmets?tafs='+stations
    username = 'bomw0004'
    password = 'defCL1M8TE'
    # if True == is_url_ok(url)   check if web site returns 200
    taf = requests.get(url, auth=(username, password)).content

    soup = BeautifulSoup(taf, 'lxml')  # parse the html
    # grab all table elements
    tables = soup.find_all('table')#, {'class':'screen'})
    # grab last table - that has all current TAFS - this may change in future
    taf = tables[-1]

    '''airports from here http://ourairports.com/countries/AU/VIC/airports.html '''
    msg = "<strong>++++++++++++++ TAF API USAGE ++++++++++++++</strong>"
    msg = msg + "<br/>" + "--> Single TAF or Multiple TAFs "
    msg = msg + "<br/>" + "<strong>tafors?taf_id=ybbn</strong> || <strong>tafors?taf_id=ybbn+yssy+ypdn+nffn</strong>"
    msg = msg + "<br/>" + "--> TAFS by area code , state or Country"
    msg = msg + "<br/>" + "<strong>tafors?area=20</strong>  ||  <strong>tafors?state=qld</strong> || <strong>tafors?cntry=fj</strong>"
    flash(msg)

    if area:
    	return render_template('tafors.html',taf=taf,area=area)
    else:
    	return render_template('tafors.html',taf=taf,area=40)  # set default area if none provided




@app.route('/plot_td/<string:sta>/', methods=['GET'])
def plot_td(sta):

    from datetime import datetime, timedelta

    from io import BytesIO
    # from flask import send_file
    # send_file throws "<built-in function uwsgi_sendfile> returned a result with an error set"
    # use Response instead
    from flask import Response
    # from werkzeug import FileWrapper
    # see https://www.pythonanywhere.com/forums/topic/13570/
    from werkzeug.wsgi import FileWrapper
    import seaborn as sns
    import matplotlib.pyplot as plt

    print("Calling plot_td with {}".format(sta))
    df = pickle.load(
        open(
            os.path.join(cur_dir, 'data', sta + '_aws.pkl'), 'rb'))


    # Plots only TD for current hour +/- 30min window

    print(datetime.utcnow(), pd.datetime.today(),format(datetime.utcnow(),'%H'),
          format(datetime.utcnow() - timedelta(minutes=30),'%H:%M'),
          format(datetime.utcnow() + timedelta(minutes=30),'%H:%M'))

    st_time = str(format(datetime.utcnow() - timedelta(minutes=30),'%H:%M'))
    end_time = str(format(datetime.utcnow() + timedelta(minutes=30), '%H:%M'))

    print( "\n\n", st_time, end_time)

    df = df.between_time(start_time= st_time, end_time  = end_time,
                         include_start=True, include_end=False)
    '''
    df = df.between_time(start_time='00:00', end_time='00:05',
                         include_start=True, include_end=False)
    '''


    try:
        os.remove(os.path.join(cur_dir,'static/images/plots', 'Td_variation_10am_swarmplot_{}.png'.format(sta)))
    except OSError:
        pass

    # plt.style.use('ggplot')
    sns.set_style('ticks')

    fig,ax = plt.subplots(figsize=(10,6))

    sns.swarmplot(ax=ax,
        x=df.loc['2000':].index.month,
        y='Td',
        hue='any_ts',
        data=df.loc['2000':])

    plt.ylim(-20,28)
    ax.set_title("Dew Point Variation between {} and {} UTC for {}\nStorm Days Vs non-Storm days by months of the Year".format(st_time,end_time,sta), color='b',fontsize=15)
    ax.set_ylabel('10am Td (C)', color='g', fontsize=20)
    ax.set_xlabel('MONTHS OF THE YEAR', color='r', fontsize=15)
    ax.tick_params(labelsize=10)

    # sns.despine()
    # fig.savefig(os.path.join(cur_dir,'static/images/plots', 'Td_variation_10am_swarmplot_{}.png'.format(sta)))

    print( "Current directory from get_avlocs() in utility_fucntions_sept2018 is", os.getcwd())

    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    w = FileWrapper(img)
    # return send_file(img, mimetype='image/png')
    return Response(w, mimetype='image/png', direct_passthrough=True)


'''
##############################################################################
Function aero_intel() is called to servce the taf intel page
when we click on any airport in the main index page  "aussie_airports.html"

When we click name of airport on the google map, it grabs the taf_id of the airport
e.g 'ybbn' and calls the aero_intel fn with the taf id as a quary parameter

'<a href="/api/v1/resources/aero_intel?taf_id=' + feature.properties.id + '">' +
feature.properties.location + '</a>'

same call place when click on airport name in table

<td><a href="/api/v1/resources/aero_intel?taf_id={{obj.LOC_ID}}">{{ obj.Location}}</a></td>
'''

# @app.route('/aero_intel/', methods=['GET'])
@app.route('/api/v1/resources/aero_intel', methods=['GET'])
def aero_intel():

    # query_parameters = request.args
    # sta = query_parameters.get('taf_id')

    if 'taf_id' in request.args:
    	sta = str(request.args['taf_id']).strip().upper()
        #if isinstance(sta, str):
        #    sta = sta.strip().upper()
    else:
        return "<h1>Error: No such TAF location, TAF ids look like YBBN, NFFN etc.</h1>"


    def percentile(n):
        def percentile_(x):
            return np.percentile(x, n)
        percentile_.__name__ = 'percentile_%s' % n
        return percentile_


    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    # from mpl_toolkits.basemap import Basemap
    import numpy as np
    time_now = datetime.utcnow()
    time_now = datetime.hour  #should be in range(24)
    # '2015-05-15 05:22:17.953439'
    print ("time now is ",time_now)
    # prints time now is  <attribute 'hour' of 'datetime.datetime' objects>

    time_now = datetime.utcnow().hour

    msg="<strong>Aerodrome Selection - type airport name  or Aviation ID - select match then Tab</strong>"
    flash(msg)
    from flask import Markup
    area = 'area40'  # hard code to area 40 for now
    if isinstance(area, str):
        area = area.strip().upper()

    '''At this stage we only serve time series and precis for qld
    locs only so need to check it location is in qld
    get aviation location info from pca and minimz database
    if requested station is not in QLD - just return taf url'''
    avlocs = bous.get_avlocs()
    '''
    if ((sta in avlocs[avlocs['State'].str.contains('QLD')].index.tolist()) \
       | (sta in avlocs[avlocs['State'].str.contains('NT')].index.tolist()) \
       | (sta in avlocs[avlocs['State'].str.contains('WA')].index.tolist())):
        pass
    else:
    '''
    if (sta not in bous.qld + bous.nt + bous.wa + bous.nsw + bous.vic + bous.sa):
        taf_url = url_for('tafors',taf_id=sta)
        # if True == is_url_ok(taf_url)   check if web site returns 200
        link = "<a href={}>{}</a>".format(taf_url,sta)
        return ("<h1>Sorry - this beta version TAF Intel prototype\
        trialled for QLD at this stage.<br>If you just after the {} TAF,\
        please use this <a href={}>link</a>.</h1>".format(sta,taf_url))
        # abort(404) will never get here as return called b4
    # Page nt yet ready for sta outside QLD = Display MSG if no page found
    # Not Found : The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

    # get all ham/sam info for this airport - sta
    airports = avlocs.reset_index() # removes av_id as index
    airports = airports.to_dict(orient='records')
    airport = ''
    found = False
    for row in airports:   # find record/row for given airport code
        if row['LOC_ID'] == sta:
            airport = row
            found = True
            print(airport)
    if not found:
        return ("<h1>Sorry to dissappoint {}: Can't locate TAF aerodrome details!</h1>".format(sta))
        #abort(404)  # no airport - means no page


    station_list = list(bous.avid_preci.items())
    default = sta

    # find closest radar site for site by calculating dist from location to each of the radar sites
    radars = {}  # store radar_url:dist pairs
    for radar in bous.radarCoords:
        # print(radar)
        radars[radar['url']]= bous.haversine( airport['Lat'], airport['Long'],radar['lat'], radar['long'])

    # print(radars)
    myList = sorted(radars.items(), key=lambda x: x[1], reverse=False)
    closest_radar_dist = myList[0][1]
    closest_radar_url = myList[0][0]

    # print(myList[0], closest_radar_dist,closest_radar_url )

    print("Calling intel/{}".format(sta))

    ob = bous.get_wx_obs_www([sta], hist='Yes')  # this wud fail for non-QLD/NT and northern WA sta
    hr,min = ob.index[-1].hour,ob.index[-1].minute   # get latest observation on the hour

    print("\n\n\n", ob.index.hour, hr,min)
    # obs = ob.loc[ob.index.hour == hr]

    obs = \
        ob.loc[
            np.logical_and(
                ob.index.hour == hr,
                ob.index.minute == min)]

    obs.columns = ['Airport', 'MSLP (hPa)', 'Temperature(C)',
                    'Dew Point Temp (C)', 'Wind Dir',
                    'Wind Spd (kts)', 'Max Gust (kts)', 'RH(%)', 'Visibility (km)']

    print("Last 3-4 days obs from /intel/sta()\n", obs.head())

    '''set up for cases where we not always have a TAF 
    or where we have a TAF location but preci location is different
    e.g for Scherger preci location is Weipa
    for Samuel Hill and Williamson its Rocky although Yepoon also good
    '''
    taf_map = {'YBSG':'YBWP', 'YBWW':'YTWB', 'YSMH':'YBRK','YWIS':'YBRK'}
    # inv_map = {v: k for k, v in taf_map.items()}

    reverse =  False  # flag for these locations
    if sta in ['YBSG', 'YBWW', 'YSMH', 'YWIS']:
        reverse = True    #sta = taf_map[sta]

    # this really ought to be a fn call - but some issues so embeded here!!!
    # taf = get_tafs(sta)
    url = 'http://reg.bom.gov.au/cgi-bin/reg/dmsu/get_tafmets?tafs='+sta
    if reverse:  # get both TAFs if possible
        url = 'http://reg.bom.gov.au/cgi-bin/reg/dmsu/get_tafmets?tafs='+sta+'+'+taf_map[sta]
        # url = 'http://reg.bom.gov.au/cgi-bin/reg/dmsu/get_tafmets?tafs='+inv_map[sta]

    '''This is a publically known login shared amongst aviation forecasters (don't freak out...)
    username = urlencode('BOMAVIATION');
    username = urlencode('1BOM2019'); '''
    username = 'bomw0004'
    password = 'defCL1M8TE'

    # catch connection errors timeouts
    # see https://opensource.com/article/17/3/python-flask-exceptions
    try:
        taf = requests.get(url, auth=(username, password)).content
        # print("Look ma no Connection Errors getting TAFs from bom.gov.au")
    except:
        # return(url_for('handle_error', error='not sure what happened. Try RELOAD page again.'))
        return('<h2>Not sure what happened. Try RELOAD page again - please!</h2>')

    soup = BeautifulSoup(taf, 'lxml')  # parse the html
    # grab all table elements
    tables = soup.find_all('table')#, {'class':'screen'})
    # grab last table - that has all current TAFS - this may change in future
    # taf = None
    taf = tables[-1]

    '''
    Above doesn't catch connection timeout errors !!!!!!!!
    from flask.ext.api import exceptions
    class ServiceUnavailable(exceptions.APIException):
        status_code = 503
        detail = 'Service temporarily unavailable, try again later.'

    try:
        taf = requests.get(url, auth=(username, password)).content
        print("Look ma no Connection Errors getting TAFs from bom.gov.au")
    except (exceptions.ConnectionError, TimeoutError, exceptions.Timeout,
                exceptions.ConnectTimeout, exceptions.ReadTimeout) as e:
        return("<h1>Error: %s. Occurred on CAS: %s. Try RELOAD page again.", (e, cas))
    '''

    # NOT GETTINNG PRECIS for now
    # forecasts=None
    # get precis for Northern GAF regions only !!! dict.keys() behave like lists
    if sta in bous.avid_preci.keys(): # bous.qld + bous.nt + bous.wa:
    #if sta in bous.qld + bous.nt + bous.wa:

        # get current preci forecasts
        if reverse:  # no preci for sta - use closest preci loc
            fcst = precis.loc[bous.avid_preci[taf_map[sta]],]
        else:
            fcst = precis.loc[bous.avid_preci[sta],]

        #If more than one av_id is mapped to one preci location
        #e.g 'YTWB':'Toowoomba','YBWW':'Toowoomba' then grab only the 1st row
        #Also note some preci issues don't have pop and rainfall !!

        if sta in ['YTWB','YWWW']:
            fcst = fcst.iloc[:7]  # get 1st 7 rows only

        for col in  ['T_max', 'T_min']:
            fcst[col] = pd.to_numeric(fcst[col], errors='coerce')

        #preci = preci.loc[
        #    pd.datetime.today().strftime('%Y-%m-%d'):
        #    (pd.datetime.today()+pd.Timedelta(1, unit='d')).strftime('%Y-%m-%d')]
        forecasts = fcst.to_html(bold_rows=True, border=4, col_space=10, justify='right', escape=False)
    else:
        forecasts=None
        # do max and min Temp plot using preci fcst

    '''
        DONT DO PLOT MAX_T WITH TIME - NO USEFUL PURPOSE!!!

        try:
            os.remove(os.path.join(cur_dir,'static/images/plots', 'max_minT_{}.png'.format(sta)))
        except OSError:
            pass

        dat =fcst[['T_max','T_min']]
        dat.fillna(method='bfill',limit=1,inplace=True)
        print(dat.describe())
        fig,ax = plt.subplots(figsize=(8,4))
        ax.plot(dat[['T_max','T_min']])
        ax.scatter(dat.index, dat['T_max'], s = 400, color='red', marker='*')
        ax.scatter(dat.index, dat['T_min'], s = 400, color='green', marker='*')

        #ax.set_ylim(ymin=np.min(dat['T_min'].values)-1,
        #            ymax=np.max(dat['T_max'].values)+1)
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%a %d')) #%b Month
        ax.fill_between(dat.index, dat['T_min'], dat['T_max'], color='y',alpha=0.1)
        ax.legend(loc='upper left')

        x=plt.gca().xaxis
        for item in x.get_ticklabels():
            item.set_rotation(45)
        plt.subplots_adjust(bottom=0.25) # adjust subplot so ticklabels don't run off the image

        ax.set_xlabel("Forecast dates")
        ax.set_ylabel("Temperature")
        if reverse:  # no preci for sta - use closest preci loc
            ax.set_title("Forecast Max/Min Temperatures at {}".format(taf_map[sta]))
        else:
            ax.set_title("Forecast Max/Min Temperatures at {}".format(sta))

        fig.savefig(os.path.join(cur_dir,'static/images/plots', 'max_minT_{}.png'.format(sta)))
    '''

    '''
    # EXTRACTING WIND CLIMATOLOGY for stations we have AWS data
    # see http://www.bom.gov.au/aviation/observations/low-level-winds/

    if sta in ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']:
        # if there is no sonde data - can't do wind climatologys
        if 'sonde_item' in session:
            # sonde_station = session.get('sonde_item')['sonde_station']
            # sonde_data from form in dict format - convert to pd Series
            sonde_data = pd.Series(session.get('sonde_item'))
        else:
            # get sonde data 1st
            try:
                # try adams database first
                sonde = getf160_adams(40842)
                sonde = sonde.resample('D').apply(get_std_levels_adams)
                sonde = process_adams_sonde(sonde).squeeze()
                sonde_data = sonde
                print("Got Sonde flight from adams")
            except:
                # so if we can't get sonde from adams, ask user for manual input
                flash(Markup('For this airport - please enter sonde data first by clicking <a href="/sonde_update" class="alert-link">here</a>'))
                return redirect(url_for('sonde_update'))

        print("\n\nEXTRACTING WIND CLIMATOLOGY\n\n")
        print("Sonde data to use for gradient wind extraction\n", sonde_data)
        grad_wnd_dir = float(sonde_data.wdir900)
        grad_wnd_spd = float(sonde_data.wspd900)
        SLP = float(sonde_data.P)

        sonde = pickle.load(
            open(os.path.join(cur_dir, 'data', 'sonde_hank_final.pkl'), 'rb'))

        print("Last days in sonde data\n", sonde.tail())

        sonde_4_period = bous.grab_data_period_centered_day_sonde(sonde, period=42)
        similar_days = bous.get_matching_days(grad_wnd_dir, grad_wnd_spd, SLP, sonde_4_period)
        print("Similar days found for low level wind climatology", len(similar_days), "\n", similar_days)

        # get aws data from station for days similar to these
        dat = pickle.load(
            open(
                os.path.join(cur_dir, 'data', sta + '_aws.pkl'), 'rb'))

        dat['date'] = dat.index.date
        sta_data_matching_days = dat.loc[dat['date'].isin(similar_days)]
        sta_data_matching_days['Hour (UTC)'] = sta_data_matching_days.index.hour
        #winds = sta_data_matching_days[['T','Td', 'Hour (UTC)']]\
        #    .groupby('Hour (UTC)').agg(['min', 'max', 'median', 'std'])
        winds = sta_data_matching_days[['T','Td', 'QNH','WS', 'WDir', 'Hour (UTC)']]\
            .groupby('Hour (UTC)').quantile([0.05,0.25, 0.75,0.95])
    '''

    '''
        # dat = dat.loc[dat['date'].isin(similar_days)]
        dat['Hour (UTC)'] = dat.index.hour
        #winds = dat[['T', 'Td', 'QNH', 'Hour (UTC)']]\
        #    .groupby('Hour (UTC)').quantile([0.05, 0.25, 0.75, 0.95])
        winds = dat[['T', 'Td', 'QNH', 'Hour (UTC)']]\
            .groupby('Hour (UTC)').agg(['min', 'max', 'median', 'std'])
        # winds = sta_data_matching_days[['WS', 'WDir', 'Hour (UTC)']].groupby('Hour (UTC)').median()

        return render_template('aerodrome_intel.html', sonde_data = sonde_data,
                        data_frame=obs.to_html(bold_rows=True,
                        border=4, col_space=10,justify='right',escape=False),
                        stat=winds.to_html(bold_rows=True,
                        border=4, col_space=10,justify='right',escape=False),
                        time_now=time_now,
                        forecasts = forecasts, hr=hr,taf=taf,area=area,airport=airport,preci_loc=bous.avid_preci[sta],\
                        station_list = station_list, closest_radar_url=closest_radar_url)
    else:
    '''
    return render_template('aerodrome_intel.html',
                        data_frame=obs.to_html(bold_rows=True,
                        border=4, col_space=10, justify='right', escape=False),
                        time_now=time_now,
                        forecasts=forecasts, hr=hr,taf=taf,area=area,airport=airport,preci_loc=bous.avid_preci[sta],\
                        station_list = station_list,closest_radar_url=closest_radar_url)


@app.route('/plot_preci/<string:state>/', methods=['GET'])
def plot_preci(state,df):

    from flask import send_file
    from io import BytesIO
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    import os
    import preci as pp
    # prepare data
    '''
    df = pp.get_precis_state(state)
    df.fillna( method='bfill',limit=1,inplace=True)
    df.set_index(keys='day', inplace=True)  
    '''
    cur_dir = '/home/accounts/vinorda/IT_stuff/python/flask_projects/storm_predictv2'

    start_date = df.index[0]
    for days_out in list(range(8)):
        end_date = (start_date + pd.Timedelta(str(days_out)+'days'))\
                        .strftime("%Y-%m-%d")

        #data = dat[dat['state'].str.contains('qld')]\
        data = df.loc[end_date, ['lat','lon','T_max']].values
        lat,lon,t_max = data[:,0],data[:,1],data[:,2]


        fig,ax = plt.subplots(figsize=(12,10))

        m = Basemap(projection='merc',llcrnrlat=-35,urcrnrlat=-8,\
            llcrnrlon=135,urcrnrlon=155,lat_ts=20,resolution='i')
        m.drawcoastlines()
        m.drawcountries()

        # draw parallels and meridians.
        parallels = np.arange(-90.,91.,5.)

        # Label the meridians and parallels
        m.drawparallels(parallels,labels=[True,False,False,False])

        # Draw Meridians and Labels
        meridians = np.arange(-180.,181.,10.)
        m.drawmeridians(meridians,labels=[True,False,False,True])
        m.drawmapboundary(fill_color='white')

        plt.title("Forecast Max Temps {0} days out from today (for {1})".format(day_out,end_date))
        x,y = m(lon, lat)
        jet = plt.cm.get_cmap('jet')

        sc = plt.scatter(x,y, c=t_max, vmin=min(t_max), vmax=max(t_max), cmap=jet, s=40, edgecolors='none')
        cbar = plt.colorbar(sc, shrink = .5)
        cbar.set_label(temp)

        # sns.despine()
        fig.savefig(os.path.join(cur_dir,'static/images/plots', 'maxT_{}.png'.format(end_date)))
        # img = BytesIO()
        # fig.savefig(img)
        # img.seek(0)
        # return send_file(img, mimetype='image/png')


@app.route('/web_cams/', methods=['GET','POST'])
def web_cams():
    #url1 = "http://avcamweb.bom.gov.au/avcam/plsql/images.display?sOptions=Y&sRegion=&sMode=HIST&nZoom=100&sTile=&sSiteNo="
    #url2= "&sDirection=ALL&nDuration=2&nFrameRate=200"
    url1= "http://avcamweb.bom.gov.au/avcam/plsql/images.display?&sOptions=Y&sSiteNo="
    url2= "&sDirection=ALL&sMode=HIST"
    # url_base = "http://avcamweb.bom.gov.au/avcam/plsql/images.display?sOptions=Y&sRegion=&sMode=HIST&nZoom=100&sTile=&sSiteNo="
    # http://avcamweb.bom.gov.au/avcam/plsql/images.display?sOptions=Y&sRegion=&sMode=HIST&nZoom=100&sTile=&sSiteNo=31011&sDirection=ALL&nDuration=2&nFrameRate=200
    '''
    web_cams = [("23034","ADELAIDE AIRPORT"),("9999","ALBANY AIRPORT"),("72160","ALBURY AIRPORT AWS"),("40211","ARCHERFIELD AIRPORT"),("87113","AVALON AIRPORT"),("40842","BRISBANE AERO"),("31011","CAIRNS AERO"),("68192","CAMDEN AIRPORT AWS"),("70351","CANBERRA AIRPORT"),("59151","COFFS HARBOUR AIRPORT"),("40717","COOLANGATTA"),("14015","DARWIN AIRPORT"),("91126","DEVONPORT AIRPORT"),("9542","ESPERANCE AERO"),("86392","GLENLITTA AVE SOUTH WEST"),("33106","HAMILTON ISLAND AIRPORT"),("94008","HOBART AIRPORT"),("200838","HOGAN ISLAND"),("27058","HORN ISLAND"),("12038","KALGOORLIE-BOULDER AIRPORT"),("88162","KILMORE GAP"),("22841","KINGSCOTE AERO"),("91311","LAUNCESTON AIRPORT"),("33045","MACKAY AERO"),("86282","MELBOURNE AIRPORT"),("76031","MILDURA AIRPORT"),("86077","MOORABBIN AIRPORT"),("68239","MOSS VALE AWS"),("63292","MOUNT BOYCE AWS"),("26021","MOUNT GAMBIER AERO"),("29127","MOUNT ISA AERO"),("61392","MURRURUNDI GAP AWS"),("200288","NORFOLK ISLAND AERO"),("23013","PARAFIELD AIRPORT"),("9021","PERTH AIRPORT"),("39083","ROCKHAMPTON AERO"),("66037","SYDNEY AIRPORT AMO"),("41529","TOOWOOMBA AIRPORT"),("72150","WAGGA WAGGA AMO"),("27045","WEIPA AERO"),("15635","YULARA AIRPORT")]
    form = webcam_inputForm()
    if form.validate_on_submit():
        st_name = (form.st_name.data)
        url = url1+st_name+url2
        return redirect(url)
        # render_template('web_cam_display.html',url=url)
    else:
        return render_template('web_cam.html', form=form)
    '''
    ''' 
    We use the airport name from aero_intel page, lookup st id of that airport
    to make URL for webcam for that airport
    '''
    station_name=''
    st_name = ''
    web_cams = {"23034":"ADELAIDE AIRPORT","9999":"ALBANY AIRPORT","72160":"ALBURY AIRPORT AWS","40211":"ARCHERFIELD AIRPORT","87113":"AVALON AIRPORT","40842":"BRISBANE AERO","31011":"CAIRNS AERO","68192":"CAMDEN AIRPORT AWS","70351":"CANBERRA AIRPORT","59151":"COFFS HARBOUR AIRPORT","40717":"COOLANGATTA","14015":"DARWIN AIRPORT","91126":"DEVONPORT AIRPORT","9542":"ESPERANCE AERO","86392":"GLENLITTA AVE SOUTH WEST","33106":"HAMILTON ISLAND AIRPORT","94008":"HOBART AIRPORT","200838":"HOGAN ISLAND","27058":"HORN ISLAND","12038":"KALGOORLIE-BOULDER AIRPORT","88162":"KILMORE GAP","22841":"KINGSCOTE AERO","91311":"LAUNCESTON AIRPORT","33045":"MACKAY AERO","86282":"MELBOURNE AIRPORT","76031":"MILDURA AIRPORT","86077":"MOORABBIN AIRPORT","68239":"MOSS VALE AWS","63292":"MOUNT BOYCE AWS","26021":"MOUNT GAMBIER AERO","29127":"MOUNT ISA AERO","61392":"MURRURUNDI GAP AWS","200288":"NORFOLK ISLAND AERO","23013":"PARAFIELD AIRPORT","9021":"PERTH AIRPORT","39083":"ROCKHAMPTON AERO","66037":"SYDNEY AIRPORT AMO","41529":"TOOWOOMBA AIRPORT","72150":"WAGGA WAGGA AMO","27045":"WEIPA AERO","15635":"YULARA AIRPORT"}

    # if this view fn  is called definitely someone clicked the webcam buuton !!!
    if request.method == "POST":
        for key in request.form:
            print("keys in webcam submit",key)
            if key.startswith('camera.'):
                station_name = key.partition('.')[-1].strip().upper()
                st_value = request.form[key]
                print("stations_name:",station_name, "name of buttton:", st_value)

        # some edge cases, there cud be others where camera name and airport location name is different
        if station_name == 'GOLD COAST':
        	station_name = 'COOLANGATTA'
        if station_name == 'AYERS ROCK (YULARA)':
        	station_name = 'YULARA AIRPORT'

        # check if successfuly extract sta name from form parameters
        if station_name:
            for id_, name in web_cams.items():
                if station_name in name:
                    st_id = id_
                    print("Found webcams name:", name, "st_id:", st_id)
                    url = url1+st_id+url2
                    print(url)
                    return redirect(url)
                    #return render_template('aerodrome_intel.html', urlparameter=url)
            else:
                #url_none = "http://avcamweb.bom.gov.au/avcam/plsql/images.display?sOptions=Y&sRegion=&sMode=HIST&nZoom=100&sTile=&sSiteNo="
                #return redirect(url_none)
                return("<h4>Sorry no webcams for {}.</h4>".format(station_name))



@app.route('/gpats_heatmaps/', methods=['GET','POST'])
def gpats_heatmaps():
    import os
    import folium
    from folium import plugins
    import gmplot
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']

    print("generate_heatmaps() view fn called")
    form = gpats_inputForm()
    if form.validate_on_submit():
        print("Gpats - form validated on post")
        dates = (form.dates.data)
        st_date,end_date = dates.split("/")
        # st_date = dates.split("/")[0]
        # end_date = dates.split("/")[1]
        print("Heatmap requested {} to {}".format(st_date, end_date))

        df = pd.read_csv('/tmp/gpats/gpats_se_qld.csv',
            header=0,
            usecols=['TM', 'LATITUDE', 'LONGITUDE'],
            index_col=['TM'],
            parse_dates=['TM'])

        df.columns = ['Lat', 'Lon']

        #data = df.loc[yr1:yr2]
        #data = data.loc[(data.index.month >= mon1) & (data.index.month <= mon2)]
        #data = data.loc[(data.index.day >= day1) & (data.index.day <= day2)]
        data = df.loc[st_date:end_date]

        # 1st delete existing heatmaps
        try:
            os.remove(os.path.join(cur_dir,'static/gpats_heatmaps',"*UTC.html"))
        except OSError:
            pass

        # Generate the heatmap into an HTML file
        # gmap.draw("/static/images/plots/gpats_heatmaps/my_heatmap.html")
        hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for hour in hours:
            dat = data.between_time(start_time = str(hour)  +':00',
                                    end_time   = str(hour+1)+':00',
                                    include_start=True, include_end=False)

            # Store our latitude and longitude
            latitudes = dat["Lat"]
            longitudes = dat["Lon"]

            # Creating the location we would like to initialize the focus on.
            # Parameters: Lattitude, Longitude, Zoom
            gmap = gmplot.GoogleMapPlotter(-27.5, 152, 7.5)

            # Overlay our datapoints onto the map
            gmap.heatmap(latitudes, longitudes)
            # for scatter plot
            # gmap.scatter(latitudes, longitudes, '#FF6666', edge_width=10)

            # Generate the heatmap into an HTML file\n",
            print(cur_dir, "\n",\
                os.path.join(cur_dir,'static/gpats_heatmaps',str(hour)+"UTC.html"))

            gmap.draw(os.path.join(cur_dir,'static/gpats_heatmaps',str(hour)+"UTC.html"))

        return render_template('gpats_heatmaps.html',st_date=st_date,hours=hours)

    else:
        return render_template('gpats_input.html', form=form)


#https://www.webforefront.com/django/usebuiltinjinjastatements.html
#https://scotch.io/bar-talk/processing-incoming-request-data-in-flask
#http://www.compjour.org/lessons/flask-single-page/multiple-dynamic-routes-in-flask/


# Date for which forecast is sought
''' get date input from main 'thunderstorm_predict.html' '''

'''
Called from main landing page
http://qld-rfc-ws45/aussy_airports/  and http://qld-rfc-ws45/
For Fog and Thunderstorm Probabilities <a href={{ url_for('storm_predict') }}  click here

Route is http://qld-rfc-ws45/thunderstorm_predictions/
renders render_template('thunderstorm_predict.html

Also re-displayed when user click of the button "TS Predictions SE QLD" on 
page http://qld-rfc-ws45/thunderstorm_predictions/ 
template/html for above page is named app/templates/thunderstorm_predict.html

Try put a Fog Predictions SE QLD button on same page
'''

@app.route('/thunderstorm_predictions/', methods=["GET", "POST"])
def storm_predict():

    '''Have overloaded/piggy backed fog prediction as this route as well
    So first up check if user clicked fog prediction button and handle that first
    by redirecting for route that handles fog calculation
    '''
    if (request.method == "POST") & ('get_fog_preds' in request.form):
        return redirect(url_for('results_FOG_seqld'))

    '''thunderstorm_predict.html template also has form to accept user feedback
    CHECK IF USER HAS pressed feedback submit button on form and handle that
    '''
    if ("post-feedback-form" in request.form):
        comment = Comment(content=request.form["contents"])
        flash("Called from index(), Comments posted", comment)
        db.session.add(comment)
        db.session.commit()

    # get here if user has pressed TS_Predictions" button - NOw deal with that
    # load observations for SE QLD for today()
    day = pd.datetime.today().strftime('%Y-%m-%d')

    stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']
    area = 'SE QLD'
    sonde_from_adams = False  #assume no sonde_data entered so far
    # check if sonde data is in - load relevant area observations/predictions only
    if 'sonde_item' in session:
        flash("#########################Loading observations for locations in current session")
        sonde_station = session.get('sonde_item')['sonde_station']
        # sonde_data from form in dict format - convert to pd Series
        sonde_data = pd.Series(session.get('sonde_item'))
        print(sonde_data)

        if sonde_station == 'YBBN':
            stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']
            area = 'Southeast QLD'
        elif sonde_station == 'YBRK':
            stations = ['YBRK', 'YGLA', 'YBUD', 'YHBA', 'YMYB', 'YTNG']
            area = 'Capricorn and Wide Bay'
        elif sonde_station == 'YBCV':
            stations = ['YBCV', 'YROM', 'YSGE', 'YTGM', 'YWDH', 'YLLE', 'YBDV']
            area = 'Southern Central and Southwest QLD'
        elif sonde_station == 'YSSY':
            stations = ['YSSY', 'YSBK', 'YSHW', 'YSCN', 'YSHL', 'YSRI', 'YWLM']

        '''
        # load default set observations for display on main index page
        flash("Loading observations for {} locations (default setup). \n\
          Predictions for locations available from last column in table \n\
          update sonde 1st!".format(area))
        observations = bous.get_wx_obs_www(stations,hist='yes')
        observations = observations.sort_index(axis=0, ascending=False)[0:len(stations)]
        observations.columns = ['Airport', 'MSLP (hPa)', 'Temperature(C)',
                    'Dew Point Temp (C)', 'Wind Dir',
                    'Wind Spd (kts)', 'Max Gust (kts)', 'RH(%)', 'Visibility (km)']

        # build url for predictions to go in last column
        av_to_pred = {}
        av_to_intel = {}
        for sta in stations:
            av_to_pred[sta] = '<a href="/results_TS_station/' + sta + '/">' + sta + '</a>'
            #av_to_intel[sta] = '<a href="/aero_intel/' + sta + '/">' + sta + '</a>'
            # av_to_intel[sta] = '<a href="/api/v1/resources/aero_intel?taf_id='+sta+'">'+sta+'</a>'
            
        observations["Get\nPredictions"] = observations['Airport'].map(av_to_pred)
        # observations['TAF Intel'] = observations['Airport'].map(av_to_intel)

        pd.set_option('display.max_columns', None)
        with open(os.path.join(cur_dir,'templates', 'observations.html'), 'w') as ob:
            observations.to_html(ob,bold_rows=True,
                        border=4, col_space=10,justify='right',escape=False)
        '''
    else:
        # we don't have any sonde data yet, try loading from adams 1st
        # if that fails throw the sonde_update to user
        try:
            sonde = bous.getf160_adams(40842) # 08180906,start_date='2018-08-07',end_date='2018-08-08')
            sonde = sonde.resample('D').apply(bous.get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            '''further post processing -
            - adjust date (23Z issue!), drop extra STN_NUM columns
            - add day of year , season, drop duplicate rows for same date'''
            sonde = bous.process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            # logger.debug("Todays sonde flight:", sonde2day)

            sonde_time = pd.to_datetime(sonde.name)#.strftime('%Y-%m-%d')
            t850 = float(sonde.T850)
            t500 = float(sonde.T500)
            QNH = sonde.P
            tmp_rate850_500 = float(t850 - t500)
            wdir_900 = sonde.wdir900
            wspd_900 = sonde.wspd900
            wdir_500 = sonde.wdir500
            wspd_500 = sonde.wspd500

            sonde_item = {'sonde_station': 'YBBN', 'sonde_time': sonde_time,
                't850': t850, 't500': t500,
                'wdir900': wdir_900, 'wspd900': wspd_900,
                'wdir500': wdir_500, 'wspd500': wspd_500,
                'tmp_rate850_500': tmp_rate850_500, 'P':QNH}
            sonde_data = pd.Series(sonde_item)

            print(sonde_item, sep='')
            session['sonde_item'] = sonde_item
            session.modified = True
            sonde_from_adams = True
            print("Sonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams == True)
        except:
            print("Having trouble getting radionsonde for",\
            day, "ENTER SONDE DATA MANUALLY on FORM")
            # FORCE USER TO ENTER SONDE DATA !!!!!!!!!!!!
            return redirect(url_for('sonde_update'))   # remark on python anywhere.com only

    if (request.method == "POST") & ('get_storm_preds' in request.form):
        if 'sonde_item' in session:
            sonde_station = session.get('sonde_item')['sonde_station']
            # sonde_data from form in dict format - convert to pd Series
            sonde_data = pd.Series(session.get('sonde_item'))
            print(sonde_data)

            if sonde_station == 'YBBN':
                stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']
                area = 'Southeast QLD'
            elif sonde_station == 'YBRK':
                stations = ['YBRK', 'YGLA', 'YBUD', 'YHBA', 'YMYB', 'YTNG']
                area = 'Capricorn and Wide Bay'
            elif sonde_station == 'YBCV':
                stations = ['YBCV', 'YROM', 'YSGE', 'YTGM', 'YWDH', 'YLLE', 'YBDV']
                area = 'Southern Central and Southwest QLD'
            elif sonde_station == 'YSSY':
                stations = ['YSSY', 'YSBK', 'YSHW', 'YSCN', 'YSHL', 'YSRI', 'YWLM']

            # prepare urls
            av_to_pred = {}
            # av_to_intel = {}
            for sta in stations:
                av_to_pred[sta] = '<a href="/results_TS_station/' + sta + '/">' + sta + '</a>'
                #av_to_intel[sta] = '<a href="/aero_intel/' + sta + '/">' + sta + '</a>'

            flash("Sonde station is {}, therefore will get predictions \
                for stations nearby {}".format(sonde_station,stations ))

            storm_predictions = bous.get_ts_predictions_stations(stations,sonde_data)
            '''print (predictions.head(1))
            sta   date       synop_days  matches  ts_cnt  prob   pred
            0  YBBN  2018-07-10    2805       52     0.0     0.0    False'''

            storm_predictions['TS Stats']  = storm_predictions['sta'].map(av_to_pred)
            #predictions['TAF Intel'] = predictions['sta'].map(av_to_intel)

            storm_predictions.columns = ['Airport', 'Date', 'Days Searched', 'Days match', \
                'TS Days', 'TS Chance ', 'Prediction', 'TS Stats']

            pd.set_option('display.max_columns', None)
            with open(os.path.join(cur_dir,'templates', 'storm_predictions.html'), 'w') as pred:
                storm_predictions.to_html(pred,bold_rows=True,
                            border=4, col_space=10,justify='right',escape=False)

            return render_template('thunderstorm_predict.html',
                day=day, stations=stations, area=area,show_obs='show', show_storm_preds='show'  ) #,comments=Comment.query.all())

        else:
            flash("No sonde data loaded yet - can't do predictions. Please load sonde data 1st")
            return redirect(url_for('sonde_update'))

            # if no sonde data better FORCE USER TO ENTER SONDE DATA !!!!!!!!!!!!
            #return render_template('thunderstorm_predict.html',day=day, stations=stations,
            #                area=area,show_obs='show' ) #,comments=Comment.query.all())

        return render_template('thunderstorm_predict.html',
            day=day, stations=stations, area=area,show_obs='show', show_preds='show'  ) #,comments=Comment.query.all())

    return render_template('thunderstorm_predict.html',day=day, stations=stations,
                            area=area,show_obs='show'  ) #,comments=Comment.query.all())


'''
GET method used by http://127.0.0.1/thunderstorm_predictions/ page
Sends data in unencrypted form to the server. Most common method.
POST method used from http://127.0.0.1/api/v1/resources/aero_intel?taf_id=YBAF
Used to send HTML form data (T and Td) to server. Data received by POST method is not cached by server.
Note that if don't have method 'POST' here then we can't post T/TD data to server to get TS predictions
'''

@app.route('/results_TS_station/<string:station>/', methods=['GET','POST'])
def results_TS_station(station):

    '''
    24hr trends in parameters such as MSLP,T,Td
    and skill of these derived parameters as predictor variables
    imagine falling pressures and rising T wud correlate
    highly with TS days and rising MSLP and falling Td with drier SE flow

    # adding single quotes around a string - just use repr()
    def foo(s1):
        return "'{}'".format(s1)
    # station = foo(station)
    '''
    from datetime import datetime
    cur_hour = datetime.utcnow().hour
    my_date = None
    station = station.upper()


    '''If we request TS calculations before 00Z, esp anytime between midnite and 10am
    the aero_intel.html template will render a form to solicit QNH and Td 
    data for that station 
    Otherwise it will just read 00Z data from station observations

    access the form data via request.form that functions like a dictionary. 
    iterate over the form key, values with request.form.items()
    '''
    if (cur_hour >= 14) & ( cur_hour <= 23.59): # just checking format of paramters from form
        print(list(request.form.items()))
        # List of tuples  --> [('press', '1019.6'), ('dewpt', '9.8')]
        for key, value in request.form.items():
            print("key: {0}, value: {1}".format(key, value))

        print("Pressure",   request.form["press"], list(request.form.items())[0][1])
        print("Dew Pt Temp",request.form["dewpt"], list(request.form.items())[1][1])

    # How to include form value in url_for function from jinja template
    # https://stackoverflow.com/questions/46509404/how-can-i-include-form-value-in-url-for-function-from-jinja-template
    # https://stackoverflow.com/questions/49130767/how-to-render-a-wtf-form-in-flask-from-a-template-that-is-included-in-another-te

    # if there is no sonde data - can't do TS predictions !!!
    if 'sonde_item' in session:
        # sonde_station = session.get('sonde_item')['sonde_station']
        # sonde_data from form in dict format - convert to pd Series
        sonde2day = pd.Series(session.get('sonde_item'))
    else:
        # get sonde data 1st
        try:
            # try adams database first
            sonde = getf160_adams(40842)
            sonde = sonde.resample('D').apply(get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            '''further post processing -
            - adjust date (23Z issue!), drop extra STN_NUM columns
            - add day of year , season, drop duplicate rows for same date'''
            sonde = process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            # logger.debug("Todays sonde flight:", sonde2day)
            sonde_from_adams = True
            sonde2day = sonde
            print("Sonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams == True)
        except:
            # so if we can't get sonde from adams, ask user for manual input
            '''
            try:
                sonde2day = pd.Series(session.get('sonde_item'))
                print("Having trouble getting radionsonde for",
                  day, "will use manually entered sonde data ", sonde2day)
                sonde_from_adams = False
                print("Sonde status", sonde_from_adams == True)
            except:
                # get sonde data 1st
            '''
            flash("No sonde data - please enter 1st")
            return redirect(url_for('sonde_update'))

    print("Getting preci for {}".format(station))
    fcst = precis.loc[bous.avid_preci[station],]
    forecasts = fcst.to_html(bold_rows=True, border=4, col_space=10, justify='right', escape=False)

    # grab only todays forecast
    preci = fcst.loc[pd.datetime.today().strftime('%Y-%m-%d')]
    #(pd.datetime.today() + pd.Timedelta(1, unit='d')).strftime('%Y-%m-%d')]

    #If more than one av_id is mapped to one preci location
    #e.g 'YTWB':'Toowoomba','YBWW':'Toowoomba' then grab only the 1st row
    #A1lso note some preci issues don't have pop and rainfall !!

    if station in ['YTWB']:
        preci = preci.iloc[0]
    # print("Preci for {}: {}".format(station,preci))
    preci_fcst = preci['preci'] + " Chance of any rain = "+ preci['pop']

    print("Processing TS stats for station {}".format(station))

    #sonde_data = pickle.load(
    #        open(os.path.join(cur_dir,'data', 'sonde_hank_final.pkl'), 'rb'))

    if station in ['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY']:
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBBN_sonde_2300_aws.pkl'), 'rb'))
            #os.path.join('app','data','sonde_hank_final.pkl'), 'rb'))
    elif station in ['YBRK','YGLA','YTNG','YBUD','YHBA','YMYB','YEML','YCMT','YMRB','YBMK','YBPN','YBHM']:
        # load Rockhampton sonde data file
        sonde_data = pickle.load( open(
            os.path.join('app','data','YBRK_sonde_2300_aws.pkl'), 'rb'))
    elif station in ['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL']:
        sonde_data = pickle.load( open(
            os.path.join('app','data','YSSY_sonde_0300_aws.pkl'), 'rb'))
        # print("\n\n\n\nBEGIN PROCESSING TS FORECASTS FOR SYDNEY BASIN\n",sonde_data.tail())
    '''
    We are matching storms based on 2300Z data, 2300Z data is actually data for following calendar day
    but we would be matching be METAR day which staarts 00Z
    so we need to reindex the donde data so we merge METAR 00Z data with correct sonde data
    No such problems using sonde data after 2300Z - as in SYd case
    '''
    if station not in ['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL']:
        sonde_data.set_index(
            keys=(sonde_data.index.date - pd.Timedelta(str(1) + ' days')),
            drop=False,inplace=bool(1))
        # we loose datetime type of index in conversion above - restore BLW
        sonde_data.index = pd.to_datetime(sonde_data.index)

    df = pickle.load(
        open(
            os.path.join(cur_dir, 'data', station + '_aws.pkl'), 'rb'))
    #print("/n/nGetting TS prediction for station: aws data is:")
    print(df.tail(1))
    #print("/nIndex of df:",df.index)
    #print("/n/nResample df:", \
    #    (df.resample('D')['AvID', 'WDir', 'WS','T', 'Td', 'QNH', 'any_ts', 'AMP'].first()).tail())
    print("/n/n00Z data only from df:", \
        df.between_time('00:00', '00:45').head()[['AvID', 'WDir', 'WS','T', 'Td', 'QNH', 'any_ts', 'AMP']])
    # merge with closest radiosonde upper data archive
    print("/nSonde data is:",sonde_data.tail(1))
    print("/nIndex of sonde data",sonde_data.index)
    '''
    File "./app/__init__.py", line 1605, in storm_predict
    storm_predictions = bous.get_ts_predictions_stations(stations,sonde_data)
    File "./utility_functions_sep2018.py", line 3047, in get_ts_predictions_stations
    left = df.resample('D')[['AvID','Td','QNH','any_ts','AMP']].first(),
    ValueError: cannot reindex from a duplicate axis
    '''
    aws_sonde_daily = pd.merge(
        #left = df.resample('D')[['AvID','Td','QNH','any_ts','AMP']].first(),
        left = df.between_time('00:00', '00:45')[['AvID','Td','QNH','any_ts']].resample('D').first(),
        right=sonde_data[['500_wdir','500_WS','T500', 'tmp_rate850_500']], #KeyError: "['500_WS', '500_wdir'] not in index"
        #right=sonde_data[['wdir500','wspd500','T500', 'tmp_rate850_500']],
        left_index=True, right_index=True,how='left')\
        .rename(columns={'QNH': 'P','any_ts':'TS','500_wdir':'wdir500','500_WS':'wspd500'})

    ''' get date input from main 'thunderstorm_predict.html' '''

    obs_4day = None

    # If date supplied - get TS predictions for that day
    # operationally - we wud always want predictions for today so my_date=''
    if my_date:
        day = pd.to_datetime(my_date)  # my_date is string like '2018-02-13'
    else:
        # If no date supplied - get prediction for TODAY
        day = pd.datetime.today()
        print("def get_ts_predictions_stations:\nNo date supplied-will try predictions for today", day)

        ## seems pointless to do this again - when we already gone thru earlier
        # but believe me without this we can get individual station prodictions from
        # aero_intel page !!!! go figure why thats the case
        try:
            # try adam 1st - will always fail on www
            sonde = getf160_adams(40842)
            sonde = sonde.resample('D').apply(get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            sonde = process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            # logger.debug("Todays sonde flight:", sonde2day)
            sonde_from_adams = True
            sonde2day = sonde
            print("Sonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams == True)
        except:
            try:
                # I think just forces check of session for sonde data
                # n finds it there now since we wud have gone sonde_update earlier
                sonde2day = pd.Series(session.get('sonde_item'))
                print("Having trouble getting radionsonde for",
                  day, "will use manually entered sonde data ", sonde2day)
                sonde_from_adams = False
                print("Sonde status from adams", sonde_from_adams == True)
            except:
                # get sonde data 1st
                flash("No sonde data - please enter 1st")
                return redirect(url_for('sonde_update'))

    # grab data for matching
    if my_date:
        # If date supplied - get prediction for that day
        day = pd.to_datetime(my_date)  # my_date is string like '2018-02-13'
        # get obs from station/sonde merged data for this date
        obs_4day = aws_sonde_daily.loc[my_date]  # .T.squeeze()
        print("Observations for given date {} is \n{}" \
              .format(day.strftime("%Y-%m-%d"), obs_4day))
    else:
        # If no date supplied - get prediction for today
        day = pd.datetime.today()
        obs_4day = sonde2day  # initialise todays obs with todays sonde
        print("\nRadio sonde for {} :\n{}"\
              .format(day.strftime("%Y-%m-%d"), obs_4day.to_frame()))
        try:

            '''Now we have already got todays sonde flight data,
            upper winds and temps and lapse rate info
            NEED to get station surface parameters from station obs'''
            # After midnight/14Z - we likely want TS forecast for next day
            # next 00Z obs not in for another 10 hours - no before 10am/00Z
            # so prompt for 00Z conditions QNH and Td all we need
            print ("Current hour is ", cur_hour)

            if ((cur_hour >= 0) & ( cur_hour < 12)):
                print("Past 00Z - so station obs for QNH and Td at 00Z should be available now")
                try:
                    wx_obs = bous.get_wx_obs_www([station]).squeeze()  # expects a list
                    print("\nObservations for 00Z on {} for {} :\n{}"\
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
                except:
                    print("\nIssues getting observartions for station:{}".format(station))
            elif (cur_hour >= 12):
                print("Past diurnal storm times for today\nThink you want predictions for tomorrow \
                    please enter forecast estimates for stations QNH and Td at 00Z")
                # press, td = input("Enter station pressure and dew point separated by comma:").strip().split(",")
                print("obs_4day B4 manual enter 00Z P,Td", obs_4day)
                obs_4day['P'] =  float(list(request.form.items())[0][1])  #float(press)
                obs_4day['Td'] = float(list(request.form.items())[1][1])
                print("\nobs_4day after manual enter 00Z P,Td\n",obs_4day)


            # when sonde data manually entered - we set these manually
            if sonde_from_adams == 0:
                print("Sonde flight from adams", sonde_from_adams,
                    "\nsonde data manually entered - we set these manually")
                obs_4day['T500'] = float(sonde2day['t500'])
                obs_4day['wdir500'] = float(sonde2day['wdir500'])
                obs_4day['wspd500'] = float(sonde2day['wspd500'])
                obs_4day['tmp_rate850_500'] = \
                    float(sonde2day['tmp_rate850_500'])
            else:
                print("Sonde flight data from adams will be used", sonde_from_adams)

            obs_4day['TS'] = None  # we don't know if curr day had TS - silly!!

            logger.debug("Observations for today {} :\n{}"\
                .format(day.strftime("%Y-%m-%d"), obs_4day))
        except:
            print("Results.html Having trouble getting station data for today for {}\
                \nTry predict TS using last obs in database".format(station))
            # obs_4day = aws_sonde_daily.loc[aws_sonde_daily.iloc[-1].index]
            # continue


    if obs_4day[['wdir500','wspd500','T500', 'P','Td','tmp_rate850_500']].isnull().any():
        logger.debug("Results.html Fix Missing parameters First")
        # Back to main landing page - focus data entry form
        flash("Results.html Fix Missing parameters 500 winds/temp and surface Td/QNH")
        return redirect(url_for('sonde_update'))
        # return redirect(url_for('aero_intel',taf_id=station))

    # ts_obs = obs_4day['TS']  # why we doing this ???
    num_days_synop = None
    search_window_obs = None
    synop_match_obs = None
    num_matches = None
    ts_day_cnt= None
    # table titles
    titles = ['na', 'Thunderstorm Days in Matchs (TS onset/end,min vis,max gust,ttl rain)',
        'Matched 10am Obs for Thunderstorm Days',
        'Matched 10am Obs but no thunderstorms']


    search_window_obs = \
        bous.grab_data_period_centered_day_sonde(aws_sonde_daily,35,day)

    try:
        num_days_synop = len(search_window_obs)
    except:
        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
        No data in season windows: VERY RARE EVENT HAS HAPPENED")
        num_days_synop = 0


    mask,synop_match_obs,num_matches,ts_day_cnt = \
        bous.calculate_percent_chance_ts_sonde(search_window_obs, obs_4day)

    logger.debug("num_matches,ts_day_cnt",num_matches,ts_day_cnt)

    if math.isnan(num_matches):
        proba = -1
        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
        No matching synop days found from {} historical days.\
        \nMust have very unusual conditions!!!"\
        .format(len(search_window_obs)))


    if math.isnan(ts_day_cnt):
        proba = -1
        logger.debug("No TS days found in matching synops."\
        .format(len(search_window_obs)))


    if (ts_day_cnt > 0):
        num_matching_days = len(synop_match_obs)
        proba = ts_day_cnt*1.0/num_matching_days
        matched_ts_dates = synop_match_obs[synop_match_obs['TS']==True].index
        matched = bous.ts_stats_based_on_aws(df,matched_ts_dates)

        aws_ts = synop_match_obs.loc[synop_match_obs['TS']==True, \
                        ['WDir', 'WS', 'T', 'Td', 'P', 'wdir500', 'wspd500', 'T500', 'tmp_rate850_500']]
        aws_no_ts = synop_match_obs.loc[synop_match_obs['TS']==False, \
                        ['WDir', 'WS', 'T', 'Td', 'P', 'wdir500', 'wspd500', 'T500', 'tmp_rate850_500']]
        tables = [matched.to_html(classes='storm'),
            aws_ts.to_html(classes='storm'),
            aws_no_ts.to_html(classes='storm-free')]
        #analogues = matched.to_html('templates/analogues.html',
        #			bold_rows = True,border=4)
        # https://pandas.pydata.org/pandas-docs/stable/style.html
        # https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
    elif (ts_day_cnt == 0):  # no matching day had storms
        logger.debug("no matching day had storms")
        num_matching_days = len(synop_match_obs)
        proba = 0.0
        aws_ts = matched = None
        aws_no_ts = synop_match_obs.loc[synop_match_obs['TS']==False,\
            ['wdir500','wspd500','T500', 'P','Td','tmp_rate850_500']]
        tables = [None,
                None,
                aws_no_ts.to_html(classes='storm-free')]
    elif (ts_day_cnt == -1): # no matching days found - very unusual!!!!
        logger.debug("no matching days found - very unusual!!!!")
        ts_day_cnt = 0
        num_matching_days = 0
        proba = -1
        aws_ts=matched=None
        aws_no_ts = None
        tables=[None,None,None]


    # check no matching days conditions 1st
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
    #y = "thunderstorm prediction is inconclusive"  if (proba == -1) else ""
    #y = "thunderstorms likely" if (proba > .15) else "thunderstorms very unlikely"

    return render_template('results_TS_prediction_station.html',
        station=station,day=day.strftime("%Y-%m-%d"),
        forecasts = forecasts,
        preci_fcst = preci_fcst,
        ts_day_cnt=ts_day_cnt,
        num_days_synop = num_days_synop,
        num_matching_days=num_matching_days,
        prediction=y,
        probability=round(proba * 100, 2),
        tables=tables,
        titles=titles)



@app.route('/results_FOG_station/<string:station>/', methods=['GET','POST'])
def results_FOG_station(station):

    '''
    24hr trends in parameters such as MSLP,T,Td
    and skill of these derived parameters as predictor variables
    imagine falling pressures and rising T wud correlate
    highly with TS days and rising MSLP and falling Td with drier SE flow

    # adding single quotes around a string - just use repr()
    def foo(s1):
        return "'{}'".format(s1)
    # station = foo(station)

    '''
    from datetime import datetime
    cur_hour = datetime.utcnow().hour
    my_date = None
    station = station.upper()
    day = pd.datetime.today()

    # av_hzd = request.args.get('hazard')

    print("Processing fog predictions for {}".format(station))

    '''If we request FG calculations before 05Z, esp anytime between midnite and 10am
    the aero_intel.html template will render a form to solicit QNH and Td
    data for that station
    Otherwise it will just read 05Z data from station observations

    access the form data via request.form that functions like a dictionary.
    iterate over the form key, values with request.form.items()

    if cur_hour > 0
        print(list(request.form.items()))
        # List of tuples  --> [('press', '1019.6'), ('dewpt', '9.8')]
        for key, value in request.form.items():
            print("key: {0}, value: {1}".format(key, value))

        print("Pressure",   request.form["press"],      list(request.form.items())[0][1])
        print("Temp",       request.form["temp"],       list(request.form.items())[1][1])
        print("Dewpt",      request.form["dewpt"],      list(request.form.items())[2][1])
        print("900_wdir",   request.form["wdir_900"],   list(request.form.items())[3][1])
        print("900_wspd",   request.form["wspd_900"],   list(request.form.items())[4][1])
        print("lr_sfc_850", request.form["lr_sfc_850"],   list(request.form.items())[5][1])
    '''

    # How to include form value in url_for function from jinja template
    # https://stackoverflow.com/questions/46509404/how-can-i-include-form-value-in-url-for-function-from-jinja-template
    # https://stackoverflow.com/questions/49130767/how-to-render-a-wtf-form-in-flask-from-a-template-that-is-included-in-another-te


    # if there is no sonde data - can't do TS predictions !!!
    if 'sonde_item' in session:
        # sonde_station = session.get('sonde_item')['sonde_station']
        # sonde_data from form in dict format - convert to pd Series
        sonde2day = pd.Series(session.get('sonde_item'))
        print("Using sonding information from current session data")
    else:
        # get sonde data 1st
        try:
            # try adams database first
            sonde = getf160_adams(40842)
            sonde = sonde.resample('D').apply(get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            #further post processing -
            #adjust date (23Z issue!), drop extra STN_NUM columns
            #add day of year , season, drop duplicate rows for same date
            sonde = process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            # logger.debug("Todays sonde flight:", sonde2day)
            sonde_from_adams = True
            sonde2day = sonde
            print("Sonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams == True)
        except:
            # so if we can't get sonde from adams, ask user for manual input

            try:
                sonde2day = pd.Series(session.get('sonde_item'))
                print("Having trouble getting radionsonde for", day,
                "will use manually entered sonde data ", sonde2day)
                sonde_from_adams = False
                print("Sonde status", sonde_from_adams == True)
            except:
            #    # get sonde data 1st
                 flash("No sonde data - please enter 1st")
                 return redirect(url_for('sonde_update'))

    print("/nGetting preci for {}".format(station))
    fcst = precis.loc[bous.avid_preci[station],]
    forecasts = fcst.to_html(bold_rows=True, border=4, col_space=10, justify='right', escape=False)

    # grab only todays forecast
    preci = fcst.loc[pd.datetime.today().strftime('%Y-%m-%d')]
    #(pd.datetime.today() + pd.Timedelta(1, unit='d')).strftime('%Y-%m-%d')]

    #If more than one av_id is mapped to one preci location
    #e.g 'YTWB':'Toowoomba','YBWW':'Toowoomba' then grab only the 1st row
    #A1lso note some preci issues don't have pop and rainfall !!

    if station in ['YTWB']:
        preci = preci.iloc[0]
    # print("Preci for {}: {}".format(station,preci))
    preci_fcst = preci['preci'] + " Chance of any rain = "+ preci['pop']

    print("***************************************************************************\
    \nProcessing Fogger stats for station {}".format(station))

    df = pickle.load(
        open(
            os.path.join(cur_dir, 'data', station + '_aws.pkl'), 'rb'))

    # get fog data - not just dates as we need to show stats for matched for days below
    fg = bous.get_fog_data_vins(station=station, auto_obs='YES')
    print("********************FOG DATA FOR "+station+"**********************************\n",fg.tail())
    fg_dates = pd.to_datetime(fg[fg['fogflag']].index.date)
    # just check the dates are same
    # fg[fg['fogflag']].index.isin(fg_dates).sum() #should return 287 fog days for YBBN
    # df.drop([fogflag], axis=1, inplace=bool(1))  maybe needed for YBBN
    #df['date'] = df.index.date
    #df['fogflag'] = df['date'].isin(fg_dates)

    print("********************FOG DATES FOR "+station+"*********************************\n")
    print('This many fog dates in aws data ', len(np.unique(fg_dates)))

    '''get ECMWF Reanal gradient level winds - we only looking at 06Z data now
    later on we can check against 12Z or 18Z data as well
    '''
    #df_winds = pd.read_csv(os.path.join('app','data','UpperWinds_QLD.csv'), parse_dates=[5], index_col=[5])
    #df_winds.drop(['u.mps', 'v.mps', 'u.kt', 'v.kt','Event.Date'], axis=1,inplace=bool(1))
    #df_winds = df_winds[df_winds['level']==900]
    #df_winds = df_winds[df_winds['Station']==station]
    #df_winds = df_winds[df_winds.index.hour == 6]
    #df_winds['Wdir'] = df_winds['Wdir'].round(0)
    #df_winds['Wdir'] = df_winds['Wdir'].astype('int')
    #df_winds.rename(columns={'Wdir': '900_wdir','Wspeed':'900_WS'}, inplace = True)

    '''Lets use sonde winds 23Z just for upper wind match
    I know this is about 5 hours after fog onset - expect little change in upper winds in that time
    Best use 5Z sounding for 06Z data, and 11Z sonding for 12Z data.
    '''
    if station in ['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB','YKRY']:
        snd = pickle.load(
            open(
            os.path.join(cur_dir, 'data', 'YBBN_sonde_2300_aws.pkl'), 'rb'))
    elif station in ['YSSY','YSRI','YWLM','YSBK','YSCN','YSHW','YSHL']:
        snd = pickle.load(
            open(
                os.path.join(cur_dir, 'data', 'YSSY_sonde_2300_aws.pkl'), 'rb'))

    # snd = bous.get_sounding_data(station='YBBN',time='23')
    # set the UTC date as index - so its same utc day as fog event
    # df_winds.set_index(df_winds.index - pd.Timedelta(str(1) + ' days'),inplace=bool(1))
    snd['lr_sfc_850'] = snd['sfc_T'] - snd['T850']
    #snd = snd[['lr_sfc_850','900_wdir','900_WS', 'T850','Td850','T700','Td700','T500','Td500']] #only grab these cols

    snd = pd.merge(left=snd, right=fg[['fogflag']],how='left',left_index=True,right_index=True)
    # df_winds.rename(columns={'wspd850':'850_WS'}, inplace = True)

    print("\b********************900hPa WIND DATA FOR "+station+"************************************************\n")
    print(snd.tail())

    obs_4day = None

    # If date supplied - get TS predictions for that day
    # operationally - we wud always want predictions for today so my_date=''
    if my_date:
        day = pd.to_datetime(my_date)  # my_date is string like '2018-02-13'
    '''
    else:
        # If no date supplied - get prediction for TODAY
        day = pd.datetime.today()
        print("def get_fogger_predictions_stations:\nNo date supplied-will try predictions for today", day)

        ## seems pointless to do this again - when we already gone thru earlier 
        # but believe me without this we can get individual station prodictions from 
        # aero_intel page !!!! go figure why thats the case
        try:
            # try adam 1st - will always fail on www
            sonde = getf160_adams(40842)
            sonde = sonde.resample('D').apply(get_std_levels_adams)
            # sonde = getf160_hanks("040842") # dont need to do std levels for hanks
            # hanks works but runs into except clause!!!

            sonde = process_adams_sonde(sonde).squeeze()
            print("Todays sonde flight for Brisbane:", sonde)
            # logger.debug("Todays sonde flight:", sonde2day)
            sonde_from_adams = True
            sonde2day = sonde
            print("Sonde flight from adams ", sonde_from_adams, " Sonde status ", sonde_from_adams == True)
        except:
            try:
                # I think just forces check of session for sonde data
                # n finds it there now since we wud have gone sonde_update earlier
                sonde2day = pd.Series(session.get('sonde_item'))
                print("Having trouble getting radionsonde for",
                day, "will use manually entered sonde data ", sonde2day)
                sonde_from_adams = False
                print("Sonde status from adams", sonde_from_adams == True)
            except:
                # get sonde data 1st
                flash("No sonde data - please enter 1st")
                return redirect(url_for('sonde_update'))

    '''
    sonde_from_adams = 0

    # grab data for matching
    if my_date:
        # If date supplied - get prediction for that day
        day = pd.to_datetime(my_date)  # my_date is string like '2018-02-13'
        # get obs from station/sonde merged data for this date
        obs_4day = aws_sonde_daily.loc[my_date]  # .T.squeeze()
        print("Observations for given date {} is \n{}" \
            .format(day.strftime("%Y-%m-%d"), obs_4day))
    else:
        # If no date supplied - get prediction for today
        day = pd.datetime.today()
        obs_4day = sonde2day  # initialise todays obs with todays sonde
        print("\nRadio sonde for {} :\n{}"\
            .format(day.strftime("%Y-%m-%d"), obs_4day.to_frame()))

        print(list(request.form.items()))
        utc=float(list(request.form.items())[0][1])
        obs_4day['P'] = float(list(request.form.items())[1][1])
        temps = list(request.form.items())[2]
        obs_4day['T'] = float(list(request.form.items())[2][1].split('/')[0])
        obs_4day['Td'] = float(list(request.form.items())[2][1].split('/')[1])
        winds_900 = list(request.form.items())[3]
        print (winds_900)  # its a tuple --> ('wind_900', '040/15'), get index 1 and split!
        obs_4day['900Dir'] = float(list(request.form.items())[3][1].split('/')[0])
        obs_4day['900spd'] = float(list(request.form.items())[3][1].split('/')[1])
        # obs_4day['lr_sfc_850'] = float(list(request.form.items())[3][1])

        '''
        try:

            #Now we have already got todays sonde flight data,
            #upper winds and temps and lapse rate info
            #BUT We NEED to parameters for 06Z
            print ("Current hour is ", cur_hour)

            
            # if (cur_hour >= 10) & ( cur_hour <= 23.59):
            if (cur_hour >= 0):
                #if av_hzd == 'FG'
                print("Not yet 06Z, please enter estimates for these variables at 06Z")
                obs_4day['P'] = float(list(request.form.items())[0][1])
                obs_4day['T'] = float(list(request.form.items())[1][1])
                obs_4day['Td'] = float(list(request.form.items())[2][1])
                obs_4day['900Dir'] = float(list(request.form.items())[3][1])
                obs_4day['900spd'] = float(list(request.form.items())[4][1])
                # obs_4day['wdir'] = wx_obs['wdir']
                # obs_4day['wspd'] = wx_obs['wspd']
            

            # when sonde data manually entered - we set these manually/kinda over-ride
            if sonde_from_adams == 0:
                print("Sonde flight from adams", sonde_from_adams,
                    "\nsonde data manually entered - we set these manually")
                obs_4day['T500'] = float(sonde2day['t500'])
                obs_4day['wdir500'] = float(sonde2day['wdir500'])
                obs_4day['wspd500'] = float(sonde2day['wspd500'])
                obs_4day['tmp_rate850_500'] = \
                    float(sonde2day['tmp_rate850_500'])
            else:
                print("Sonde flight data from adams will be used", sonde_from_adams)

            obs_4day['FG'] = None  # we don't know if curr day had FG - silly!!
            logger.debug("Observations for today {} :\n{}" \
                .format(day.strftime("%Y-%m-%d"), obs_4day))
        except:
            print("Results.html Having trouble getting station data for today for {}\
                \nTry predict TS using last obs in database".format(station))
            # obs_4day = aws_sonde_daily.loc[aws_sonde_daily.iloc[-1].index]
            # continue
        '''
    # df_temp = df.loc[df.index.hour == 18]  # filter out 18Z obs from stations AWS obs data b4 merging in
    # df_temp = df.loc[np.logical_and(df.index.hour == 6, df.index.minute == 0)]
    # df_temp = df_temp.resample('D').first()  # gets only one 06XX UTC obs from each day
    # note the above keeps 'fogflag' as bool but introduces some NaN which can make filtering paninful
    df_temp=None
    if utc==5:
        df_temp = df.between_time('04:45', '05:15').resample('D').first()
        print("Matching using 3pm data\n",df[['T','Td','QNH']].between_time('04:45', '05:15').tail())
    if utc==8:
        df_temp = df.between_time('07:45', '08:15').resample('D').first()
        print("Matching using 6pm data\n",df[['T','Td','QNH']].between_time('07:45', '08:15').tail())
    if utc==11:
        df_temp = df.between_time('10:45', '11:15').resample('D').first()
        print("Matching using 6pm data\n",df[['T','Td','QNH']].between_time('10:45', '11:15').tail())
    if utc==14:
        df_temp = df.between_time('13:45', '14:15').resample('D').first()
        print("Matching using 6pm data\n",df[['T','Td','QNH']].between_time('13:45', '13:15').tail())
    df_temp = df_temp.loc[:df.index.date[-1]]  # resample introduces days for rest of days in year!!
    # df_temp['fogflag'] = df_temp['fogflag'].astype(bool)  # force to be boolean converts NaN to False
    # Now this would work to filter fog days only ==>  df_temp[df_temp['fogflag']]

    aws_sonde_daily = pd.merge(
        left=df_temp[['AvID', 'T', 'Td', 'WS', 'WDir', 'QNH']], \
        right=snd[['900_wdir', '900_WS', 'lr_sfc_850', 'fogflag']], \
        left_index=True, right_index=True, how='left')

    print("********************FINAL AWS + 900 WINDS MERGED DATA FOR "+station+"********************************\n")
    print('Final fogger merged file\n', aws_sonde_daily[aws_sonde_daily['fogflag']==1].tail())

    #if obs_4day[['P','T','Td','900Dir','900spd','lr_sfc_850']].isnull().any():
    if obs_4day[['P', 'T', 'Td', '900Dir', '900spd']].isnull().any():
        logger.debug("Results.html Fix Missing parameters First")
        # Back to main landing page - focus data entry form
        flash("Results.html Fix Missing parameters Gradient (900hPa) Winds and Surface T/Td/QNH")
        return redirect(url_for('aero_intel',taf_id=station))

    num_days_synop = None
    search_window_obs = None
    synop_match_obs = None
    num_matches = None
    num_matching_days = None
    fg_day_cnt= None
    # table titles
    titles = ['','TD - Dewpoint Temperature Thresholds','QNH - MSLP Thresholds',\
        'Fog Days in Matchs (FG onset/end,min vis,max gust,ttl rain)', \
        'Matched 17Z Obs for Fog Days','Matched 17Z Obs but no fogs']

    # day = pd.datetime.today()
    # we use current day to center our search on current calendar day/month
    search_window_obs = \
        bous.grab_data_period_centered_day_sonde(aws_sonde_daily,35,day)
    try:
        num_days_synop = len(search_window_obs)
    except:
        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
        No data in season windows: VERY RARE EVENT HAS HAPPENED")
        num_days_synop = 0


    mask,synop_match_obs,num_matches,fg_day_cnt = \
        bous.calculate_percent_chance_fg_sonde(search_window_obs.copy(), obs_4day)

    ''' return (mask,matching_synops,
                num_of_days_match_synop_pattern,num_of_FG_days)'''

    logger.debug("num_matches,fog_day_cnt",num_matches,fg_day_cnt)
    print("num_matches,fog_day_cnt",num_matches,fg_day_cnt)
    synop_match_obs.dropna(subset=['fogflag'],inplace=bool(1))
    print("Matched synop days fog/no_fog counts\n",synop_match_obs['fogflag'].value_counts())

    day = pd.datetime.today()
    cur_month = day.month
    month_list = [cur_month-1,cur_month,cur_month+1]
    print(f'Current day={day}, current month={cur_month}, month_list={month_list}')

    print(fg.loc[fg.index.month.isin(month_list)].tail(),"\n",\
          fg.loc[fg.index.month.isin(month_list), ['rain_flag', 'fogflag', 'Td5', 'Td8', 'Td11', 'Td14']].tail(),"\n",\
          fg.loc[fg.index.month.isin(month_list), ['rain_flag', 'fogflag', 'QNH5', 'QNH8', 'QNH11', 'QNH14']].tail())

    td_thresh = fg.loc[fg.index.month.isin(month_list), ['rain_flag','fogflag','Td5','Td8','Td11','Td14']].\
        groupby(['rain_flag','fogflag']).\
        quantile(q=(0.2,0.5,0.8)).transpose()

    msl_thresh = fg.loc[fg.index.month.isin(month_list), ['rain_flag','fogflag','QNH5','QNH8','QNH11','QNH14']].\
        groupby(['rain_flag','fogflag']).\
        quantile(q=(0.2,0.5,0.8)).transpose()

    if math.isnan(num_matches):
        proba = -1
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
        No matching synop days found from {} historical days.\
            \nMust have very unusual conditions!!!"\
                .format(len(search_window_obs)))

    if math.isnan(fg_day_cnt):
        proba = -1
        print("No FOG days found in matching synops."\
            .format(len(search_window_obs)))


    if (fg_day_cnt > 0):

        print("fg_day_cnt > 0.")
        num_matching_days = len(synop_match_obs)
        proba = fg_day_cnt*1.0/num_matching_days
        matched_fg_dates = synop_match_obs.loc[synop_match_obs['fogflag']].index.date
        print(f'These are days that had fog, {synop_match_obs.loc[synop_match_obs["fogflag"]].index.date}')
        print(f'Number of matched_fg_dates = {len(matched_fg_dates)}')
        '''
        matched_non_fg_dates = synop_match_obs.loc[~(synop_match_obs['fogflag'])].index
        gives some really nasty index errors 
        KeyError: "None of [Int64Index([-1,-1, -1,., -2, -1, -1],dtype='int64', name='date')] are in the [index]"
        '''
        # use set operation - index difference to get the non-fog dates!!
        matched_non_fg_dates = sorted(list((set(synop_match_obs.index.date)).difference(set(matched_fg_dates))))
        print(f'These are days that had no fog: {matched_non_fg_dates}, Length {len(matched_non_fg_dates)}')

        matched = fg.loc[matched_fg_dates]

        aws_ts = synop_match_obs.loc[matched_fg_dates, \
                ['T', 'Td', 'WS', 'WDir', 'QNH', 'fogflag','900_wdir','900_WS','lr_sfc_850']]
        aws_no_ts = synop_match_obs.loc[matched_non_fg_dates,\
                ['T', 'Td', 'WS', 'WDir', 'QNH', 'fogflag','900_wdir','900_WS','lr_sfc_850']]
        tables = [td_thresh.to_html(), msl_thresh.to_html(),\
            matched.to_html(classes='storm'),\
            aws_ts.to_html(classes='storm'),\
            aws_no_ts.to_html(classes='storm-free')]


        #analogues = matched.to_html('templates/analogues.html',
        #			bold_rows = True,border=4)
        # https://pandas.pydata.org/pandas-docs/stable/style.html
        # https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html

    elif (fg_day_cnt == 0):  # no matching day had storms
        logger.debug("no matching day had fog")
        num_matching_days = len(synop_match_obs)
        proba = 0.0
        aws_ts = matched = None
        aws_no_ts = synop_match_obs.loc[synop_match_obs['fogflag'] == False, \
            ['WDir', 'WS', 'T', 'Td', 'P', 'lr_sfc_850']]
        tables = [td_thresh.to_html(), msl_thresh.to_html(),None, None,aws_no_ts.to_html(classes='storm-free')]


    elif ((math.isnan(fg_day_cnt))|(fg_day_cnt == -1)): # no matching days found - very unusual!!!!
        logger.debug("no matching days found - very unusual!!!!")
        fg_day_cnt = 0
        num_matching_days = 0
        proba = -1
        aws_ts=matched=None
        aws_no_ts = None
        tables=[td_thresh.to_html(), msl_thresh.to_html(),None,None,None]


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

    return render_template('results_FOG_station.html',
        station=station,day=day.strftime("%Y-%m-%d"),
        forecasts = forecasts,
        preci_fcst = preci_fcst,
        fg_day_cnt=fg_day_cnt,
        num_days_synop = num_days_synop,
        num_matching_days=num_matching_days,
        prediction=pred,
        probability=round(proba * 100, 2),
        tables=tables,
        titles=titles)



@app.route('/results_TS_seqld', methods=['POST'])
def results_TS_seqld():
    if 'sonde_item' in session:
        station = session.get('sonde_item')['sonde_station']
        # sonde_data from form in dict format - convert to pd Series
        # sonde_data = pd.Series(session.get('sonde_item'))
    else:
        # get sonde data 1st
        return redirect(url_for('sonde_update'))

    #stations = ['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB']
    stations = ['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB']
    #predictions = bous.get_ts_predictions_stations(stations,'2017-02-14')
    storm_predictions = bous.get_ts_predictions_stations(stations)

    #open(os.path.join(cur_dir,
    #             'data', station+'_aws.pkl'), 'rb')

    with open(os.path.join(cur_dir,'templates', 'predictions.html'), 'w') as pred:
        stprm_predictions.to_html(pred,bold_rows=True,
                        border=4, col_space=10,justify='right',escape=False)

    # predictions.to_html('predictions.html',
    #   			bold_rows = True,border=2)
    # https://pandas.pydata.org/pandas-docs/stable/style.html
    # https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html

    return render_template('results_TS_seqld.html')


@app.route('/results_FOG_seqld', methods=['GET'])
def results_FOG_seqld():

    # stations = ['YBBN','YBAF','YAMB','YBSU','YBCG','YBOK','YTWB']
    stations = ['YBBN', 'YBAF', 'YAMB', 'YBSU', 'YBCG', 'YBOK', 'YTWB']
    # predictions = bous.get_ts_predictions_stations(stations,'2017-02-14')
    fog_predictions = bous.get_fg_predictions_stations_new(stations)

    # open(os.path.join(cur_dir,
    #             'data', station+'_aws.pkl'), 'rb')

    with open(os.path.join(cur_dir, 'templates', 'fog_predictions.html'), 'w') as pred:
        fog_predictions.to_html(pred, bold_rows=True,
                            border=4, col_space=10, justify='right', escape=False)

    return render_template('results_FOG_seqld.html')




@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    # db.create_all()  # make our sqlalchemy tables
    # app.run(debug=True)
    app.run(host='0.0.0.0',debug=True)

'''
# INSTEAD OF ABOVE WE JUST HAVE
app = Flask(__name__)# instantiate an object of class Flask
# to start the debugger and reloader - set debug attribute of the application instance (app) to True
app.debug = True
app = Flask(__name__)
app.config["DEBUG"] = True
'''
