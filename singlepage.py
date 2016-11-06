from flask import *
from flask.views import *
from serializer import *


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
            app.add_url_rule(
                self.endpoint, view_func=cls.as_view(self.endpoint))
            cls.object = cls
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

    def dispatch_request(self):
        if request.method == 'GET':
            response, class_type = self.get()
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'POST':
            response, class_type = self.post()
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'PUT':
            response, class_type = self.put()
            return jsonify({'data': serializer.dump(response, class_type)})
        elif request.method == 'DELETE':
            response, class_type = self.delete()
            return jsonify({'data': serializer.dump(response, class_type)})
