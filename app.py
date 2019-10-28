# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
import sys

import click
from flask import Flask
from flask import redirect, url_for, abort, render_template, flash,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField,StringField
from wtforms.validators import DataRequired,Optional,Regexp, Length,InputRequired
from flask_migrate import Migrate
import re
from flask_debugtoolbar import DebugToolbarExtension

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'mysql://'
else:
    prefix = 'mysql://'

app = Flask(__name__)



app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'szy1996')
toolbar = DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix+'root:Liting2017@localhost/cs608'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(fighters = Fighters, models = Models, weapons = Weapons,\
         companies = Companies, engines = Engines,\
         equippedwithengines = Equippedwithengines, equippedwithweapons=Equippedwithweapons)

# Regexp Pattern
input_pattern = re.compile('^[0-9a-zA-Z]+[\-\/]?[0-9a-zA-Z]*[\-\/]?[0-9a-zA-Z]*$')
space_pattern = re.compile('\\s+')

oneprilist = ['Companies','Fighters','Models','Weapons','Engines']
multiplyprelist = ['Equippedwithengines','Equippedwithweapons']
# Models
class Fighters(db.Model):
    __tablename__ = 'fighters'

    name = db.Column(db.String(40), primary_key=True)
    number_built = db.Column(db.Integer)
    generation = db.Column(db.String(40))
    number_of_engine = db.Column(db.Integer)
    designedby = db.Column(db.String(40),db.ForeignKey('companies.name') )

    models = db.relationship('Models',cascade='save-update, delete')

    Equippedwithweapons = db.relationship('Equippedwithweapons',cascade='save-update, delete')
    Equippedwithengines = db.relationship('Equippedwithengines',cascade='save-update, delete')
    # optional
    def __repr__(self):
        return '<fighters>' 


class Models(db.Model):
    __tablename__ = 'models'

    name =  db.Column(db.String(40), primary_key=True)
    first_flight = db.Column(db.Integer)
    status = db.Column(db.String(15))
    fighter_name = db.Column(db.String(40), db.ForeignKey('fighters.name') )

    Equippedwithweapons = db.relationship('Equippedwithweapons',cascade='save-update, delete')
    Equippedwithengines = db.relationship('Equippedwithengines',cascade='save-update, delete')

class Weapons(db.Model):
    __tablename__ = 'weapons'

    name = db.Column(db.String(40), primary_key=True)
    year = db.Column(db.Integer)
    country =  db.Column(db.String(40))
    type = db.Column(db.String(40))

    Equippedwithweapons = db.relationship('Equippedwithweapons',cascade='save-update, delete')
    
class Companies(db.Model):
    __tablename__ = 'companies'

    name =  db.Column(db.String(40), primary_key=True)
    start = db.Column(db.Integer)
    over = db.Column(db.Integer, nullable = True)
    country = db.Column(db.String(40))

    Fighters = db.relationship('Fighters',cascade='save-update, delete')

class Engines(db.Model):
    __tablename__  = 'engines'

    name =  db.Column(db.String(40), primary_key=True)
    year = db.Column(db.Integer)
    country =  db.Column(db.String(40))

    Equippedwithengines = db.relationship('Equippedwithengines',cascade='save-update, delete')

class Equippedwithweapons(db.Model):
    __tablename__ = 'equippedwithweapons'
    fighter_name = db.Column(db.String(40), db.ForeignKey('fighters.name'),primary_key=True)
    model_name = db.Column(db.String(40), db.ForeignKey('models.name'),primary_key=True)
    weapon_name = db.Column(db.String(40), db.ForeignKey('weapons.name'),primary_key=True)

class Equippedwithengines(db.Model):
    __tablename__ = 'equippedwithengines'
    fighter_name = db.Column(db.String(40), db.ForeignKey('fighters.name'),primary_key=True)
    model_name = db.Column(db.String(40), db.ForeignKey('models.name'),primary_key=True)
    engine_name = db.Column(db.String(40), db.ForeignKey('engines.name'),primary_key=True)

def GetDatabase(database_name):

    database_list = ['Companies','Fighters','Models','Weapons','Engines',\
        'Equippedwithengines','Equippedwithweapons']   
    if database_name in database_list:

        database = dict(Fighters = Fighters, Models = Models, Weapons = Weapons,\
            Companies = Companies, Engines = Engines,\
            Equippedwithengines = Equippedwithengines, Equippedwithweapons=Equippedwithweapons)
        return database[database_name]


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# Forms

class TestForm(FlaskForm):
    body = TextAreaField('Body')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')

from queryfunc import queryfunc

@app.route('/')
def index():
    database = ['Companies','Fighters','Models','Weapons','Engines','Equippedwithengines','Equippedwithweapons']
    form = DeleteNoteForm
    return render_template('index.html',database = database,form = form)

@app.route('/show/<string:database_name>',methods=['GET'])
def show_data(database_name):
    database = GetDatabase(database_name)
    attrslist = []
    for columns in database.__table__.columns:
        attrslist.append(columns.key)

    return render_template('show.html',\
        attrs = attrslist, querydata=list(database.query.all()),database_name=database_name)    

@app.route('/show/<string:database_name>/<string:attr_name>',methods=['GET'])
def show_data_byorder(database_name,attr_name):
    database = GetDatabase(database_name)
    attrslist = []
    for columns in database.__table__.columns:
        attrslist.append(columns.key)

    return render_template('show.html',\
        attrs = attrslist, querydata=list(database.query.order_by(database.__dict__[attr_name]).all()),database_name=database_name)    

    

@app.route('/search/<string:database_name>',methods = ['GET','POST'])
def search_data(database_name):
    class SearchDataForm(FlaskForm):
        pass
    
    database = GetDatabase(database_name)
    for columns in database.__table__.columns:
        setattr(SearchDataForm, str(columns.key),StringField(str(columns.key),\
             validators = [Length(min=0, max=40,message='input length must be 0-40')]))
    
    setattr(SearchDataForm,'submit_btn',SubmitField('Submit'))

    form = SearchDataForm()

    if form.validate_on_submit():
        queryname = []
        queryval = []
        emptyflag = 0
        attrslist = []
        for field in list(form)[:-2]:
            attrslist.append(field.name)
            if field.data != "" and input_pattern.match(field.data):
                queryname.append(database.__dict__[field.name])
                queryval.append(field.data)
                emptyflag += 1
            
        if emptyflag:
            querydata = queryfunc(database,emptyflag,[queryname,queryval])
        else:
            flash('Input invalid data')
            return redirect(url_for('index'))
        # bug
        return render_template('search_result.html',\
            attrs = attrslist, querydata=list(querydata),database_name=database_name)
    return render_template('search.html',form = form, \
        database_name = database_name) 



@app.route('/new/<string:database_name>', methods=['GET', 'POST'])
def new_data(database_name):

    class NewDataForm(FlaskForm):
        pass
    
    database = GetDatabase(database_name)
    for columns in database.__table__.columns:
        if columns.key != 'over':
            setattr(NewDataForm, str(columns.key),StringField(str(columns.key),\
                    validators = [Length(min=0, max=40,message='input length must be 0-40'),\
                    Regexp(regex=input_pattern,message='invalid input'),\
                    InputRequired(message='input can not be empty')]))
        else:
             setattr(NewDataForm, str(columns.key),StringField(str(columns.key),\
                    validators = [Length(min=0, max=40,message='input length must be 0-40')]))           
    
    setattr(NewDataForm,'submit_btn',SubmitField('Submit'))
    form = NewDataForm()

    if form.validate_on_submit():
        attrsdict = dict()
        for field in list(form)[:-2]:
            if field.name == 'over':
                if input_pattern.match(field.data):
                    attrsdict[field.name] = field.data
                else:
                    attrsdict[field.name] = None
            else:
                attrsdict[field.name] = field.data
        data = database(**attrsdict)
        db.session.add(data)
        
        # try:
        #     db.session.commit()
        #     flash('Your note is saved.')            
        # except:
        #     flash('Invalid, check relationship.')   

        db.session.commit()
        flash('Your note is saved.') 

        return redirect(url_for('index'))
    return render_template('new.html', form=form,database_name=database_name)


@app.route('/edit/<string:database_name>', methods=['GET', 'POST'])
def edit_data(database_name):
    class NewDataForm(FlaskForm):
        pass
    
    database = GetDatabase(database_name)
    for columns in database.__table__.columns:
        if columns.primary_key == True:
            setattr(NewDataForm, str(columns.key),StringField(str(columns.key),\
                validators = [Length(min=0, max=40,message='input length must be 0-40'),\
                    Regexp(regex=input_pattern,message='invalid input'),\
                    InputRequired(message='input can not be empty')]))

    setattr(NewDataForm,'submit_btn',SubmitField('Submit'))
    form = NewDataForm()

    if form.validate_on_submit():
        for field in list(form)[:1]:
            data = database.query.get(field.data)
            name = field.data
        if data == None:
            flash('No data, please check first')
            return redirect(url_for('index'))
        else:
            flash('Data found')
            return redirect(url_for('edit_data_input', database_name=database_name, prikey=name ))

    return render_template('edit.html', form=form,database_name=database_name)

@app.route('/edit/<string:database_name>/<string:prikey>', methods=['GET', 'POST'])
def edit_data_input(database_name,prikey):
    class NewDataForm(FlaskForm):
        pass
    
    database = GetDatabase(database_name)
    data = database.query.get(prikey)
    attrsdict = dict()
    

    for columns in database.__table__.columns:
        if columns.primary_key == True:
            priname = columns.key
            continue

        attrsdict[columns.key] = data.__dict__[columns.key]

 
        setattr(NewDataForm, str(columns.key),StringField(str(columns.key),\
                    render_kw={'placeholder': str(data.__dict__[columns.key]) },\
                    validators = [Length(min=0, max=40,message='input length must be 0-40')]))
        
    
    setattr(NewDataForm,'submit_btn',SubmitField('Submit'))
    form = NewDataForm()

    if form.validate_on_submit():
        for field in list(form)[:-2]:
            if input_pattern.match(field.data):
                # bug
                if attrsdict[field.name] != field.data:
                    attrsdict[field.name] = field.data
        changed = database.query.update(attrsdict)
        db.session.commit()
        flash('Your note is updated.') 
        return redirect(url_for('index'))
    return render_template('edit_submit.html', form=form,database_name=database_name, prikey = prikey, priname = priname)





@app.route('/delete/<string:database_name>', methods=['GET','POST'])
def delete_data(database_name):
    delete_form = DeleteNoteForm()
    class SearchDataForm(FlaskForm):
        pass
    
    database = GetDatabase(database_name)
    prikey = ''
    for columns in database.__table__.columns:
        if database_name in oneprilist:
            if columns.primary_key == True:
                prikey = columns.key
        else:
            if columns.primary_key == True:
                prikey = prikey + columns.key + ' '

        setattr(SearchDataForm, str(columns.key),StringField(str(columns.key),\
             validators = [Length(min=0, max=40,message='input length must be 0-40')]))
    
    setattr(SearchDataForm,'submit_btn',SubmitField('Submit'))

    form = SearchDataForm()

    if form.validate_on_submit():
        queryname = []
        queryval = []
        emptyflag = 0
        attrslist = []
        for field in list(form)[:-2]:
            attrslist.append(field.name)
            if field.data != "" and input_pattern.match(field.data):
                queryname.append(database.__dict__[field.name])
                queryval.append(field.data)
                emptyflag += 1
            
        if emptyflag:
            querydata = queryfunc(database,emptyflag,[queryname,queryval])
        else:
            flash('Input invalid data')
            return redirect(url_for('index'))
        # bug
        return render_template('delete_list.html',\
            attrs = attrslist, querydata=list(querydata),database_name=database_name,form = delete_form,prikey=prikey)
    return render_template('search.html',form = form, \
        database_name = database_name) 


@app.route('/delete/<string:database_name>/<prikey>/<prikeyname>', methods=['POST'])
def delete_data_btn(database_name,prikey,prikeyname):
    form = DeleteNoteForm()
    database = GetDatabase(database_name)
    delete_dict = dict()

    if database_name in oneprilist:
        delete_dict[prikeyname] = prikey
    else:
        prikeyname = prikeyname.split(' ')
        prikey = prikey.split(' ')
        for i in zip(prikeyname, prikey):
            delete_dict[i[0]] = i[1]

    if form.validate_on_submit():
        target = database.query.filter_by(**delete_dict).first()
        db.session.delete(target)
        db.session.commit()
        flash('Your note is deleted.')
    else:
        abort(400)
    return redirect(url_for('index'))




# # event listening
# class Draft(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     edit_time = db.Column(db.Integer, default=0)


# @db.event.listens_for(Draft.body, 'set')
# def increment_edit_time(target, value, oldvalue, initiator):
#     if target.edit_time is not None:
#         target.edit_time += 1

# same with:
# @db.event.listens_for(Draft.body, 'set', named=True)
# def increment_edit_time(**kwargs):
#     if kwargs['target'].edit_time is not None:
#         kwargs['target'].edit_time += 1


        #   {% if database_name in ['Companies','Fighters','Models','Weapons','Engines'] %}    
        #     <form method="post" action="{{ url_for('delete_data_btn', database_name=database_name, prikey = data.__dict__[prikey],prikeyname = prikey) }}">
        #         {{ form.csrf_token }}
        #         {{ form.submit(class='btn') }}
        #     </form>  
        #   {% else %}
        #   <form method="post" action="{{ url_for('delete_data_btn', database_name=database_name, prikey =data.__dict__[attrs[0]]+' '+data.__dict__[attrs[1]]+' '+data.__dict__[attrs[2]],prikeyname = attrs[0]+' '+attrs[1]+' '+attrs[2] )}}">
        #         {{ form.csrf_token }}
        #         {{ form.submit(class='btn') }}
        #   </form>  
        #   {% endif %}