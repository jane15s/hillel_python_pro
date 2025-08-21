from xmlrpc.client import DateTime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Date
from database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    password = Column(String(50))
    email = Column(String(120), unique=True)
    birth_date = Column(Date)
    gender = Column(String(10))

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r} surname={self.surname!r} email={self.email!r}>"

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    def __repr__(self):
        return f"<Category id={self.id} name={self.name!r} owner={self.owner}>"

class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    category = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    amount = Column(Numeric)
    datetime =Column(DateTime)
    owner = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    type = Column(Integer)

    def __repr__(self):
        return (f"<Transactions id={self.id} description={self.description!r} "
                f"category={self.category} amount={self.amount} "
                f"datetime={self.datetime} owner={self.owner} type={self.type}>")