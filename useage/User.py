# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum
# 注册url


@url('/users/')
class User(GeneralViewWithSQLAlchemy, Base):
    # 配置数据库会话链接
    db_session = db_session
    # 定义delete方法是真实删除还是软删除
    real_delete = False
    # 定义数据表
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    telephone = Column(String(15))
    nickname = Column(String(20))
    _pwd = Column(String(50))
    deleted = Column(Boolean())
    # 定义哪些字段不由前端填充
    __in_exclude__ = ['id', '_pwd', 'deleted']
    # 定义哪些字段不展示给前端
    __exclude__ = ['_pwd']
    # 定义属性装饰方法
    __property__ = {'pwd': '_pwd'}

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, value):
        self._pwd = u'假装加密' + value
