# coding: utf-8
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataBase(object):
    '''

        Class for interaction with database

    '''

    _dir_name = os.path.dirname(__file__)
    DB_URLS = {
        u'people': 'sqlite:///' + _dir_name + '/../databases/people.db',
        u'logs': 'sqlite:///' + _dir_name + '/../databases/logs.db'
    }

    def __init__(self, url):
        self.engine = create_engine(url, echo=False)

    def new_session(self):
        return sessionmaker(bind=self.engine)()