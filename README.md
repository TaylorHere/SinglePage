# SinglePage
this is a RESTful framework of flask ,you can just write a singe page ,then you done your job
framework dependencies:
    flask
###this project start at 1024 of 2016
this is what we want  
useage dependecies:
    flask
    sqlalchemy
~~~python
# coding: utf-8
from singlepage import *
from singlepage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum

# 注册url


@url('/user')
class User(SinglePage, Base):
    # 定义数据表
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    telephone = Column(String(15))
    nickname = Column(String(20))
    __exclude__ = ['id']
    # 处理http get方法

    def get(self):
        # 查询数据
        return db_session.query(self.object).all(), 'sqlalchemy'
    # 处理http post方法

    def post(self):
        # 获取request的json并新建一个用户
        data = request.get_json()
        user = self.object(data)
        db_session.add(user)
        db_session.commit()
        return 'ok', 'basic'
# 注册这个APP
User()
# 启动服务器
if __name__ == '__main__':
    app.run(debug=True)
~~~
