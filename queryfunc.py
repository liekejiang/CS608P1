

import os
import sys

import click
from flask import Flask
from flask import redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField,StringField
from wtforms.validators import DataRequired,Optional,Regexp, Length
from flask_migrate import Migrate
from sqlalchemy import and_, or_
import re


def queryfunc(database,para_num,para_list):
    if para_num == 1:
        result = database.query.filter(para_list[0][0]==para_list[1][0])
    elif para_num == 2:
        result = database.query.filter(and_(para_list[0][0]==para_list[1][0],\
            para_list[0][1]==para_list[1][1]))
    elif para_num == 3:
        result = database.query.filter(and_(para_list[0][0]==para_list[1][0],\
            para_list[0][1]==para_list[1][1],\
            para_list[0][2]==para_list[1][2]))
    elif para_num == 4:
        result = database.query.filter(and_(para_list[0][0]==para_list[1][0],\
            para_list[0][1]==para_list[1][1],\
            para_list[0][2]==para_list[1][2],\
            para_list[0][3]==para_list[1][3]))
    elif para_num == 5:
        result = database.query.filter(and_(para_list[0][0]==para_list[1][0],\
            para_list[0][1]==para_list[1][1],\
            para_list[0][2]==para_list[1][2],\
            para_list[0][3]==para_list[1][3],\
            para_list[0][4]==para_list[1][4]))
    return result 