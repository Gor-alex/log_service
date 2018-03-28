# coding: utf-8
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
metadata = Base.metadata


class Person(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(Text)
    last_name = Column(Text)
    gender = Column(Text)

    @hybrid_property
    def full_name(self):
        return self.first_name + u' ' + self.last_name