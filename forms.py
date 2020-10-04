'''
WTForms is a powerful framework-agnostic (framework independent) library
written in Python. It allows us to generate HTML forms,
validate forms, pre-populate form with data (useful for editing) and so on.
In addition to that it also provides CSRF protection.


Flask-WTF is a Flask Extension which integrates Flask with WTForms.
Flask-WTF also provides some additional features like File Uploads,
reCAPTCHA, internationalization (i18n) and so on.

We define our forms as Python classes.
Every form class must extend the FlaskForm class of the flask_wtf package.
The FlaskForm is a wrapper containing some useful methods around the original
wtform.Form class, which is the base class for creating forms.
Inside the form class, we define form fields as class variables.

Form fields are defined by creating an object associated with the field type.
The wtform package provides several classes which represent form fields
like StringField, PasswordField, SelectField, TextAreaField, SubmitField etc.
'''
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
from wtforms import TextField, DecimalField, TextAreaField, SubmitField, RadioField, SelectField

class Sonde_updateForm(FlaskForm):

   st_name = RadioField('Sonde station',
                        choices = [('YBBN','Brisbane'),('YBCV','Charleville'),
                                ('YBRK','Rockhampton')],
                    validators=[DataRequired("Not valid choice of stations")],
                    default = 'YBBN')

   sonde_time = SelectField('Sonde Time',
                        choices = [('05Z', '3PM Afternoon Sonde'),
                                   ('23Z', '9AM Mid Morning Sonde')],
                    validators=[DataRequired("Not valid choice of sounding times")],
                    default = '23Z')

   QNH = TextField("Mean Sea Level Pressure",\
                       validators=[DataRequired("Please enter MSLP (hPa).")],default = '1020')

   t850 = TextField("850hPa Temperature",\
                       validators=[DataRequired("Please enter 850 temperature.")],default = '10')
   t500 = TextField("500hPa Temperature",\
                       validators=[DataRequired("Please enter 500 temperature.")],default = '-10')

   wnd900 = TextField("Gradient Level winds e.g 340/20",\
                       validators=[DataRequired("Please enter 900 winds in format DDD/SS.")],default = '340/20')

   wnd500 = TextField("500hPa winds e.g 340/20",\
                       validators=[DataRequired("Please enter 500 winds in format DDD/SS.")],default = '340/20')

   submit = SubmitField("Update")



class gpats_inputForm(FlaskForm):
   dates = TextField("Date range e.g for 3rd Oct 2010 to 12 Sept 2018, enter 2010-10-03/2018-09-12",\
                       validators=[DataRequired("Make sure dates in format YYYY-MM-DD seperate by fwd slash- ")])
   submit = SubmitField("Enter")


# we have not really used this form
class webcam_inputForm(FlaskForm):
    web_cams = [("23034","ADELAIDE AIRPORT"),("9999","ALBANY AIRPORT"),("72160","ALBURY AIRPORT AWS"),("40211","ARCHERFIELD AIRPORT"),("87113","AVALON AIRPORT"),("40842","BRISBANE AERO"),("31011","CAIRNS AERO"),("68192","CAMDEN AIRPORT AWS"),("70351","CANBERRA AIRPORT"),("59151","COFFS HARBOUR AIRPORT"),("40717","COOLANGATTA"),("14015","DARWIN AIRPORT"),("91126","DEVONPORT AIRPORT"),("9542","ESPERANCE AERO"),("86392","GLENLITTA AVE SOUTH WEST"),("33106","HAMILTON ISLAND AIRPORT"),("94008","HOBART AIRPORT"),("200838","HOGAN ISLAND"),("27058","HORN ISLAND"),("12038","KALGOORLIE-BOULDER AIRPORT"),("88162","KILMORE GAP"),("22841","KINGSCOTE AERO"),("91311","LAUNCESTON AIRPORT"),("33045","MACKAY AERO"),("86282","MELBOURNE AIRPORT"),("76031","MILDURA AIRPORT"),("86077","MOORABBIN AIRPORT"),("68239","MOSS VALE AWS"),("63292","MOUNT BOYCE AWS"),("26021","MOUNT GAMBIER AERO"),("29127","MOUNT ISA AERO"),("61392","MURRURUNDI GAP AWS"),("200288","NORFOLK ISLAND AERO"),("23013","PARAFIELD AIRPORT"),("9021","PERTH AIRPORT"),("39083","ROCKHAMPTON AERO"),("66037","SYDNEY AIRPORT AMO"),("41529","TOOWOOMBA AIRPORT"),("72150","WAGGA WAGGA AMO"),("27045","WEIPA AERO"),("15635","YULARA AIRPORT")]
    st_name = SelectField('Web Cam Location',
                        choices = web_cams,
                    validators=[DataRequired("Not valid choice of stations")],
                    default = "40842")    
    submit = SubmitField("Update")

