from sqlalchemy import Column
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from . import BaseModel


class AdminModel(BaseModel):
    __tablename__ = 'acc'
    username = Column(String(16), nullable=True)
    password = Column(String(128), nullable=True)
