from flask import *
from flask.views import *
from serializer import *
import inspect
import sys


class Model():
    """a pluggable model base here"""
    base = None

model = Model()

app = Flask(__name__)


class url(object):

    def __init__(self, endpoint=''):
        self.endpoint = endpoint

    def __call__(self, cls):
        def _call(*args, **kw):
            view = cls.as_view(cls.__name__)
            cls.pk_list = {}
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
                    print self.endpoint + '<' + arg + '>'
            cls.object = cls
            app.add_url_rule(self.endpoint, view_func=view)

            print self.endpoint
        return _call


class SinglePage(View):
    """this is the base class of single page,
    it's a combine of flask's Methond view and some kind of DB's base class(instance)"""
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def __init__(self, json=None):
        if json is not None:
            class_dict = serializer.attr_dict_from_sqlalchemy(self)
            for item in class_dict:
                setattr(self, item, json[item])

    def dispatch_request(self, *args, **kwargs):
        if request.method == 'GET':
            if kwargs == {}:
                kwargs = {self.pk_list['get']: None}
            response, class_type = self.get(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'POST':
            if kwargs == {}:
                kwargs = {self.pk_list['post']: None}
            response, class_type = self.post(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'PUT':
            if kwargs == {}:
                kwargs = {self.pk_list['put']: None}
            response, class_type = self.put(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'DELETE':
            if kwargs == {}:
                kwargs = {self.pk_list['delete']: None}
            response, class_type = self.delete(*args, **kwargs)
            return jsonify({'data': serializer.dump(response, class_type)})
