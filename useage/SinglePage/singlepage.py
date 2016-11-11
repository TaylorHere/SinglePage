# coding: utf-8
from flask import *
from flask.views import *
from serializer import *
import inspect
import sys

app = Flask(__name__)
app.config['resources'] = {}


class url(object):

    def __init__(self, endpoint=''):
        self.endpoint = endpoint

    def __call__(self, cls):
        def _call(*args, **kw):
            view = cls.as_view(cls.__name__)
            cls.pk_list = {}
            resource_name = self.endpoint.replace('/', '')
            app.config['resources'].update({resource_name: cls})
            for method in cls.methods:
                lowcase_method = method.lower()
                try:
                    func = getattr(cls, lowcase_method)
                except AttributeError, e:
                    pass
                args = []
                defaults = []
                if inspect.getargspec(func)[0] is not None:
                    args = [e for e in inspect.getargspec(
                        func)[0] if e is not 'self']

                if inspect.getargspec(func)[3] is not None:
                    defaults = [e for e in inspect.getargspec(
                        func)[3] if e is not 'self']
                defaults_dict = dict([(arg, default)
                                      for arg in args for default in defaults])
                for arg in args:
                    cls.pk_list.update({lowcase_method: arg})
                    app.add_url_rule(self.endpoint + '<' + arg + '>',
                                     view_func=view, defaults=defaults_dict, methods=[method, ])
                    print lowcase_method + ' ' + self.endpoint + '<' + arg + '>'
            cls.object = cls
            app.add_url_rule(self.endpoint, view_func=view)
            return cls()
        return _call


class SinglePage(View):
    """this is the base class of single page"""
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def __init__(self, json=None):
        if json is not None:
            class_dict = serializer.attr_dict_from_sqlalchemy_in_exclude(self)
            for item in class_dict:
                setattr(self, item, json[item])

    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if kwargs == {}:
                try:
                    kwargs = {self.pk_list['get']: None}
                except KeyError, e:
                    pass
            response, class_type = self.get(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'POST':
            if kwargs == {}:
                try:
                    kwargs = {self.pk_list['post']: None}
                except KeyError, e:
                    pass
            response, class_type = self.post(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'PUT':
            if kwargs == {}:
                try:
                    kwargs = {self.pk_list['put']: None}
                except KeyError, e:
                    pass
            response, class_type = self.put(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'DELETE':
            if kwargs == {}:
                try:
                    kwargs = {self.pk_list['delete']: None}
                except KeyError, e:
                    pass
            response, class_type = self.delete(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})


class permission():

    def get(self, request, pk):
        'get permission'
        return True

    def post(self, request):
        'post permission'
        return True

    def put(self, request, pk):
        'put permission'
        return True

    def delete(self, request, pk):
        'delete permission'
        return True


class GeneralViewWithSQLAlchemy(SinglePage):
    """docstring for GeneralView"""
    db_session = None
    real_delete = False
    __in_exclude__ = []
    # 定义哪些字段不展示给前端
    __exclude__ = []
    # 定义属性装饰方法
    __property__ = {}
    __permission__ = [permission]
    # 处理http get方法

    def filter(self, query, value):
        """
        等于 key = value
        不等于 key != value
        boolean 值 Flase：0，True：1
        大于 key > value
        小于 key < value
        或 expression A or expression B
        且 expression A and expression B
            ex:
                'name = taylor and and age <20 and deleted = 0'
        """
        from sqlalchemy import text

        return query.filter(text(value))

    def asc_order_by(self, query, value):
        from sqlalchemy import text

        return query.order_by(text(value))

    def desc_order_by(self, query, value):
        from sqlalchemy import desc
        from sqlalchemy import text

        return query.order_by(desc(text(value)))

    def limit(self, query, value):
        return query[0:int(value)]

    def fileds(self, query, value):
        pass

    # 过滤器实现于args名称字典
    __query_args__ = {'filter': filter, 'asc_order_by': asc_order_by,
                      'desc_order_by': desc_order_by, 'limit': limit, 'fileds': fileds}

    def get(self, pk):
        # 查询数据
        un_passed_permissions = [p for p in self.__permission__ if p().get(request, pk)
                                 is False]
        if not un_passed_permissions:
            if pk is not None:
                query = self.db_session.query(
                    self.object).filter(self.object.id == pk)
                # for arg in self.__query_args__:
                #     value = request.args.get(arg, None)
                #     query = self.__query_args__[arg](query, value)
                return query, 'sqlalchemy'
            else:
                query = self.db_session.query(self.object)
                for arg in self.__query_args__:
                    value = request.args.get(arg, None)
                    if value is not None:
                        query = self.__query_args__[arg](self, query, value)
                return query, 'sqlalchemy'
        else:
            return "permission hint: " + ''.join([p.get.__doc__ for p in un_passed_permissions]), 'basic'
    # 处理http post方法

    def post(self, query):
        # 获取request的json并新建一个用户
        un_passed_permissions = [p for p in self.__permission__ if p().post(request)
                                 is False]
        if not un_passed_permissions:
            data = request.get_json()
            obj = self.object(data)
            self.db_session.add(obj)
            self.db_session.commit()
            return obj, 'sqlalchemy'
        else:
            return "permission hint: " + ''.join([p.post.__doc__ for p in un_passed_permissions]), 'basic'

    def delete(self, pk):
        un_passed_permissions = [p for p in self.__permission__ if p().delete(request, pk)
                                 is False]
        if not un_passed_permissions:
            if self.real_delete:
                if pk is not None:
                    self.db_session.query(self.object).filter(
                        self.object.id == pk).delete()
                    self.db_session.commit()
                    return self.db_session.query(self.object).filter(
                        self.object.id == pk), 'sqlalchemy'
                else:
                    return 'need pk', 'basic'
            else:
                if pk is not None:
                    print pk
                    self.db_session.query(self.object).filter(
                        self.object.id == pk).update({self.object.deleted: True})
                    self.db_session.commit()
                    return self.db_session.query(self.object).filter(
                        self.object.id == pk), 'sqlalchemy'
                else:
                    return 'need pk', 'basic'
        else:
            return "need permission: " + ''.join([p.delete.__doc__ for p in un_passed_permissions]), 'basic'

    def put(self, pk):
        un_passed_permissions = [p for p in self.__permission__ if p().put(request, pk)
                                 is False]
        if not un_passed_permissions:
            if pk is not None:
                query = self.db_session.query(self.object).filter(
                    self.object.id == pk)
                data = request.get_json()
                properties = [d for d in data if d in self.__property__]
                for d in properties:
                    setattr(self, d, data[d])
                    value = getattr(self, d)
                    del data[d]
                    data[self.__property__[d]] = value
                query.update(data)
                self.db_session.commit()
                return self.db_session.query(self.object).filter(
                    self.object.id == pk), 'sqlalchemy'
            else:
                return 'need pk', 'basic'
        else:
            return "permission hint: " + ''.join([p.put.__doc__ for p in permissions]), 'basic'
