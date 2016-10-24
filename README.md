# SinglePage
this is a RESTful framework of flask ,you can just write a singe page ,then you done your job
###this project start at 1024 of 2016
this is what we want  
~~~python
from SinglePage import SinglePage, Model
app = SinglePage()



@app.route('/')
# the simple stence above dinfine the url of this model
class User(Model):
    name = xxx
    age = xxx
    pwd = xxx
    # above, dinfine a table of the database

    def __init__(self, name=None, age=None, pwd=None):
        self.name = name
        self.age = age
        self.pwd = pwd
    # above, dinfine the store process

    def get(session, args, json):
        return session[User.name == json.name].first()

    def post(session, args, json):
        return session.add(User.add(json))

    def delete(session, args, json):
        return session.delete(User.name == json.name)

    # when you use http to access this url(model),the method you use will map
    # on the same name function
    # and the args and json body will across to the function as well
    # you just need to write the business logic,then return.
    # yep ,we will handle the serializer.
~~~
