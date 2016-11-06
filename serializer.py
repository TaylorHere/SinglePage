class Serializer():

    def dump(self, origin_instance, class_type='sqlalchemy'):
        # class_type choice 'sqlalchemy', 'basic'
        self.class_type = class_type
        if self.class_type == 'sqlalchemy':
            origin_instance = [instance for instance in origin_instance]
            return self.typping(origin_instance)
        elif self.class_type == 'basic':
            return self.typping(origin_instance)

    def cycling(self, instance):

        if isinstance(instance, (set, list)):
            m_list = []
            for item in instance:
                value = self.typping(item)
                m_list.append(value)
            return m_list
        if isinstance(instance, dict):
            m_dict = {}
            for item in instance:
                value = self.typping(instance[item])
                m_dict.update({item: value})
            return m_dict

    def typping(self, instance):

        if isinstance(instance, set):
            return self.cycling(instance)
        elif isinstance(instance, list):
            return self.cycling(instance)
        elif isinstance(instance, dict):
            return self.cycling(instance)
        elif isinstance(instance, (float, int, basestring, bool)):
            return instance
        elif instance is None:
            return None
        else:
            return self.typping(self.mapping(instance))

    def mapping(self, instance):
        if self.class_type == 'basic':
            return self.attr_dict_from_basic(instance)
        elif self.class_type == 'sqlalchemy':
            return self.attr_dict_from_sqlalchemy(instance)

    def attr_dict_from_basic(self, instance):
        try:
            exclude = [e for e in instance.__exclude__]
        except:
            exclude = []

        full = dict([[e, getattr(instance, e)] for e in dir(instance)
                     if not e.startswith('_') and not hasattr(
                         getattr(instance, e), '__clall__') and e not in exclude])
        propery = dict([[p, getattr(instance, e).__get__(instance, type(instance))]
                        for p in full if hasattr(full[p], 'fset')])

        full.update(propery)
        return full

    def attr_dict_from_sqlalchemy(self, instance):
        try:
            exclude = [e for e in instance.__exclude__]
        except:
            exclude = []

        full = dict([[e, instance.__getattribute__(e)]
                     for e in instance.__mapper__.c.keys() if e not in exclude])
        return full
serializer = Serializer()


def serializer_decotator(f, class_type='sqlalchemy'):
    """warp the return and serialize to json"""
    def decorator(*args, **kwargs):
        return jsonify({'data': serializer.typping(f(*args, **kwargs), class_type)})
    return decorator
