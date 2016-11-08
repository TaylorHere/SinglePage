# coding:utf-8
from User import User
from Address import Address
from SinglePage import app
# 注册APP
# 启动服务器
User()
Address()
if __name__ == '__main__':
    app.run(debug=True)
