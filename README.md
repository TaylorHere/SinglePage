# Document for SingePage

SingePage 是一个基于flask的python RESTful 框架

源代码很简单，容易修改与扩展

使用简单，提供GeneralView，完全不用管json部分



框架目前主要类，描述列表如下：

|            类名             |                    用途                    |
| :-----------------------: | :--------------------------------------: |
|            url            |                给View注册url                |
|        SinglePage         |       基于flask.view，提供请求分发，结果序列化功能        |
| GeneralViewWithSQLAlchemy | 基于SinglePage类的通用视图函数，能和SQLAlchemy配合快速实现接口 |
|        permission         |           用于视图访问权限管理，可用来实现业务逻辑           |



## 快速开始

与flask常用的基于方法的视图不同，SinglePage的常规用法是基于类

~~~python
# coding: utf-8
from SinglePage import app, SinglePage
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum

class Address(SinglePage, Base):
    pass
~~~

以上代码片段，从SinglePage导入flask实例，SinglePage类，导入数据库相关

我们的Address类继承至SinglePage，同时继承了来自SQLAlchemy的Base，这样这个类同时是视图和ORM

当然目前这份代码没有任何作用，我们继续完善它，首先定义字段

~~~python
# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum

class Address(SinglePage, Base):
    # 定义表字段
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    address = Column(String(15))
~~~

新增的代码定义了表名字，主键id，address

既然这是一个RESTful框架，那么应该能够方便的响应HTTP动词，事实上在SinglePage内部实现了请求分发，不同动词的请求会由不同的方法来响应，目前支持，**PUT,GET,POST,DELETE** ,四种常用的方法，他们会分别由同名但是小写的方法来响应，代码如下。

~~~python
# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum

class Address(SinglePage, Base):
    # 定义数据表
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    address = Column(String(15))

    # 处理http get方法
    def get(self):
        return db_session.query(self.object).all(), 'sqlalchemy'

    # 处理http post方法
    def post(self):
        # 获取request的json并新建一个用户
        data = request.get_json()
        address = self.object(data)
        db_session.add(address)
        db_session.commit()
        return 'ok', 'basic'

~~~

以上代码处理了GET和POST方法，当对应的请求到来时会分别由get(),post()来响应

其中get方法会把数据库中所有address表记录返回，post方法会新增一条记录

你可能注意到了，return语句很奇怪。

~~~python
return db_session.query(self.object).all(), 'sqlalchemy'
return 'ok', 'basic'
~~~

第一条语句返回了查询队列和字符串‘sqlalchemy’，第二条队列返回了字符串’ok‘和字符串’basic‘

事实上SinglePage处理了动词响应方法的返回，它会将这些返回进行序列化和JSON化，由于序列化器实现的原因，必须指明带序列对象的类型，目前支持的序列化对象包括sqlalchemy的普通类，他们对应使用'sqlalchemy'和'basic'来注明，字符串，数据包装类都属于‘basic’，当然，我知道，这很不优雅。

第二个让人遗憾的地方应该是self.object，它指向类自身，注意self.object得到的不是类实例而是类本身。

所以以下代码：

~~~python
data = request.get_json()
address = self.object(data)
~~~

 获取来自请求中的json数据，self.object(data),实际上执行了Address的实例化操作，SinglePage为我们提供了映射，它会自动把我们定义的id，和address字段作为json中的key，去获取json中的值，并完成创建SQLAlchemy对象的操作。

ok，到这里，我们已经有了数据库，表定义，和接口规则，那么URL呢？

~~~python
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

    # 处理http get方法
    def get(self, address_id):
        # 查询数据
        if address_id is not None:
            return db_session.query(self.object).filter(self.object.id == address_id), 'sqlalchemy'
        else:
            return db_session.query(self.object).all(), 'sqlalchemy'

    # 处理http post方法
    def post(self):
        # 获取request的json并新建一条地址
        data = request.get_json()
        address = self.object(data)
        db_session.add(address)
        db_session.commit()
        return 'ok', 'basic'
if __name__ = '__main__':
	Address()
    app.run()
~~~

使用@语法可以轻松的注册把Address注册到路由系统，URL中请一定带上结尾的'/'。

接下来在启动这个python脚本，Adders()这个实例化操作，会把Address真正的注册到路由系统中，然后访问http:127.0.0.1:5000/addresses/便可以使用这个视图了。

## 更RESTful的使用URL

RESTful应该按如下方式来使用URL

| URL           | HTTP动词 | 功能        |
| ------------- | ------ | --------- |
| /addresses/   | GET    | 获取所有数据    |
| /addresses/id | GET    | 获取对应id的数据 |
| /addresses/   | POST   | 新增一条      |
| /addresses/id | PUT    | 更新对应id的数据 |

想要使用id，只需要在对应方法里增加一个参数，id变会注册到路由系统中，如下：

~~~python
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
~~~

我们便有了/addresses/address_id这样一条url你可以用以下方式使用它

~~~python
/addresses/address_id=1
/addresses/1
~~~

两种方法中的1最终都会映射到get方法中的参数address_id上面

如果仅仅访问/addresses/那么这个参数为None，所以你不用设置默认值为None

## 不需要客户端知道东西

上文提到过self.object()会知道把Address中定义的字段作为json数据的key去获取json里面的值，然后实例化一个ORM对象，那么你可以回疑问，难道id也要由客户端传入吗？

当然我们做了一下简单的措施来防止客户端填充不需要的字段

~~~python
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
    __in_exclude__ = ['id']
    __exclude__ = ['id']
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

~~~

~~~python
__in_exclude__
~~~

这个列表内的字符串，标注了不需要由客户端填充的字段

~~~python
__exclude__
~~~

这个列表内的字符串，标注了不会返回给客户端的字段，

## 实例化这步我有话说

或许自动生成ORM实例这步，会影响到你处理一些字段数据，比如客户端发来密码而你打算将密码hash之后再存储，那么你可以使用python的属性方法以及SinglePage的属性方法字典

~~~python
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
if __name__ == '__main__':
    User()
    app.run()
~~~

以上代码的效果是，客户端拥有一个/users/接口，可以轻松使用HTTP动词执行数据的增删改查

并且，每次pwd字段变动时都会进行在客户端值的基础上加上‘假装加密‘这样的前缀，

~~~python
# 定义哪些字段不由前端填充
__in_exclude__ = ['id', '_pwd', 'deleted']
# 定义哪些字段不展示给前端
__exclude__ = ['_pwd']
# 定义属性装饰方法
__property__ = {'pwd': '_pwd'}
~~~

这三条语句指明了不需要客户端填充的字段，和不需要展示给客户端的字段，以及_pwd字段的属性方法为pwd

客户端使用POST时只需提交：

~~~json
{
    "nickname":"TayloeHere",
    "telephone":"151****8887",
    "pwd":"00000"
}
~~~

使用GET时会收到到如下类似的数据：

~~~json
{
  "data": [
    {
      "deleted": null,
      "id": 1,
      "nickname": "TaylorHere",
      "pwd": "假装加密00000",
      "telephone": "151****8887"
    }
  ]
}
~~~

细心的你可能会发现User类是基于GeneralViewWithSQLAlchemy实现的

这个类提供了通用的视图，并按RESTful的风格提供URL和返回，同时提供了软删除选项，当然这需要你定义一个叫做deleted的boolean型字段。

通用视图提供的URL如下（以User类为例）:

| URL       | HTTP动词 | 功能        |
| --------- | ------ | --------- |
| /users/   | GET    | 获取所有数据    |
| /users/id | GET    | 获取对应id的用户 |
| /users/   | POST   | 新增一条      |
| /users/id | PUT    | 更新对应id的用户 |



## 权限管理

~~~python
class permission():

    def get(self, request):
        'get permission'
        return True

    def post(self, request):
        'post permission'
        return True

    def put(self, request):
        'put permission'
        return True

    def delete(self, request):
        'delete permission'
        return True
~~~

以上为permission源代码，一个permission可以控制一个视图不同动作函数的访问权限，准确说是访问这个动作后，是否执行动作内代码的权限。

使用时只需继承permission类，并重载对应动作方法，返回True则为权限通过，返回false为权限不通过，

最后将你的权限类注册到\__permission__列表中，一个视图可以拥有多个权限类，同时，权限动作方法中的注释会被作为权限不同时的默认返回。

~~~python
# coding: utf-8
from SinglePage import *
from SinglePage import app
from base import Base, db_session
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum
# 注册url


@url('/users/')
class User(GeneralViewWithSQLAlchemy, Base):

    class UserPermission(permission):
        """author:Taylor<tank357@icloud.com>"""

        def get(self, request):
            'do not open this api'
            return False
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
    __permission__ = [UserPermission]

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, value):
        self._pwd = u'假装加密' + value

~~~



## 未来

SinglePage是花草秀团队目前正在开发中的RESTful框架，接下来，我们将会为改框架添加更多的特性，使其更符合商业用例。

