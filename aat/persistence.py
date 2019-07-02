from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship

# Base sqlalchemy
Base = declarative_base()


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
