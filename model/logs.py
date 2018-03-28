# coding: utf-8
from sqlalchemy import Column, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import re


Base = declarative_base()
metadata = Base.metadata


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, unique=True)
    dt = Column(Float)
    event = Column(Text)

    @hybrid_property
    def persons(self):
        persons = set()
        for start, number, end in re.findall(r'(<p=)(\d+)(>)', self.event):
            persons.add(int(number))

        return persons