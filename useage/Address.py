# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum

# 注册url


@url('/addresses/')
class Address(SinglePage, Base):
    # 定义数据表
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    address = Column(String(15))
    # __exclude__ = ['id']
    # 处理http get方法

    def get(self, address_id):
        # 查询数据
        if address_id is not None:
            return db_session.query(self.object).filter(self.object.id == address_id), 'sqlalchemy'
        else:
            return db_session.query(self.object).all(), 'sqlalchemy'
    # 处理http post方法

    def post(self):
        # 获取request的json并新建一个用户
        data = request.get_json()
        address = self.object(data)
        db_session.add(address)
        db_session.commit()
        return 'ok', 'basic'
