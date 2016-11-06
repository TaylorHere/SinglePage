# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum
# 注册url


@url('/users/')
class User(SinglePage, Base):
    # 定义数据表
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    telephone = Column(String(15))
    nickname = Column(String(20))
    # __exclude__ = ['id']
    # 处理http get方法

    def get(self, user_id):
        # 查询数据
        if user_id is not None:
            return db_session.query(self.object).filter(self.object.id == user_id), 'sqlalchemy'
        else:
            return db_session.query(self.object).all(), 'sqlalchemy'
    # 处理http post方法

    def post(self):
        # 获取request的json并新建一个用户
        data = request.get_json()
        user = self.object(data)
        db_session.add(user)
        db_session.commit()
        return 'ok', 'basic'

    def delete(self, user_id):
        if user_id is not None:
            db_session.query(self.object).filter(
                self.object.id == user_id).delete()
            return db_session.query(self.object).filter(
                self.object.id == user_id), 'sqlalchemy'
        else:
            return 'need user_id', 'basic'
