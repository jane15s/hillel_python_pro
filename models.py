from xmlrpc.client import DateTime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    password = Column(String(50))
    email = Column(String(120), unique=True)

    def __repr__(self):
        return f'<User {self.name!r}>'

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    category = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    amount = Column(Numeric)
    datetime =Column(DateTime)
    owner = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    type = Column(Integer)