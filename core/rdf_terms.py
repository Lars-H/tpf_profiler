class RDF_term(object):

    def __init__(self, **kwargs):
        if "@id" in kwargs:
            return URI(kwargs['@id'], namespaces=kwargs['namespaces'])
        else:
            return Literal(kwargs)

    @property
    def value(self):
        pass

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(type(self)) + ": " + str(self)


class URI(RDF_term):

    def __init__(self, uri, **kwargs):
        if 'namespaces' in kwargs:
            if not ("http://" in uri or "https://" in uri):
                uri = kwargs['namespaces'][uri.split(
                    ":")[0]] + uri.split(":")[1]
        self._URI = uri

    @property
    def value(self):
        return self._URI

    def __str__(self):
        return str(self._URI)


class Literal(RDF_term):

    def __init__(self, **kwargs):
        self._value = kwargs.get("@value", "")
        self._type = kwargs.get("@type", "")
        self._language = kwargs.get("@language", "")

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    @property
    def lang(self):
        return self._language

    def __str__(self):
        return str(self.value) + " " + str(self.type)


class Variable(RDF_term):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self.value)


class Triple(object):

    def __init__(self, s, p, o):
        self._subject = s
        self._predicate = p
        self._object = o

    @property
    def subject(self):
        return self._subject

    @property
    def predicate(self):
        return self._predicate

    @property
    def object(self):
        return self._object

    @property
    def variables(self):
        vars = []
        if type(self.subject) == Variable:
            vars.append(self.subject)
        if type(self.object) == Variable:
            vars.append(self.object)
        if type(self.predicate) == Variable:
            vars.append(self.predicate)
        return vars

    @property
    def contains_literal(self):
        if type(self._object) == Literal:
            return True
        else:
            return False

    def __iter__(self):
        yield self

    def __repr__(self):
        return str(self.subject) + " " + str(self.predicate) + " " + str(self.object) + "."

    @property
    def dict(self):
        return {
            'subject' : str(self.subject),
            'predicate': str(self.predicate),
            'object': str(self.object),
        }
