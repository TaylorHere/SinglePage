# coding:utf-8
import sys
sys.path.append('..')
from User import User
from Address import Address
from SinglePage import app
# 注册APP
User()
Address()
# 启动服务器
if __name__ == '__main__':
    app.run(debug=True)
