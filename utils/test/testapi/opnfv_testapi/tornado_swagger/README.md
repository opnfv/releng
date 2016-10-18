# tornado-swagger

## What is tornado-swagger?
tornado is a wrapper for tornado which enables swagger-ui support.

In essense, you just need to wrap the Api instance and add a few python decorators to
get full swagger support.http://swagger.io/


## How to use:


```python
from tornado.web import RequestHandler, HTTPError
from tornado_swagger import swagger

swagger.docs()

# You may decorate your operation with @swagger.operation and use docs to inform information
class ItemNoParamHandler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self):
        """
            @param body: create test results for a item.
            @type body: L{Item}
            @return 200: item is created.
            @raise 400: invalid input
        """

# Operations not decorated with @swagger.operation do not get added to the swagger docs

class ItemNoParamHandler(GenericApiHandler):
    def options(self):
        """
        I'm not visible in the swagger docs
        """
        pass


# Then you use swagger.Application instead of tornado.web.Application
# and do other operations as usual

def make_app():
    return swagger.Application([
        (r"/items", ItemNoParamHandler),
        (r"/items/([^/]+)", ItemHandler),
        (r"/items/([^/]+)/cases/([^/]+)", ItemOptionParamHandler),
    ])

# You define models like this:
@swagger.model
class Item:
    """
        @descriptin:
            This is an example of a model class that has parameters in its constructor
            and the fields in the swagger spec are derived from the parameters to __init__.
        @notes:
            In this case we would have property1, property2 as required parameters
            and property3 as optional parameter.
        @property property3: Item decription
        @ptype property3: L{PropertySubclass}
    """
    def __init__(self, property1, property2=None):
        self.property1 = property1
        self.property2 = property2

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "property1",
            ],
            "properties": [
                "property1": {
                    "type": "string"
                },
                "property2": {
                    "type": "string"
                    "default": null
                }
            ]
        }
    }

# If you declare an __init__ method with meaningful arguments
# then those args could be used to deduce the swagger model fields.
# just as shown above

# if you declare an @property in docs, this property property2 will also be used
# to deduce the swagger model fields
class Item:
    """
        @property property3: Item description
    """
    def __init__(self, property1, property2):
        self.property1 = property1
        self.property2 = property2

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "property1",
            ],
            "properties": [
                "property1": {
                    "type": "string"
                },
                "property2": {
                    "type": "string"
                }
                "property3": {
                    "type": "string"
                }
            ]
        }
    }

# if you declare an argument with @ptype, the type of this argument will be specified
# rather than the default 'string'
class Item:
    """
        @ptype property3: L{PropertySubclass}
    """
    def __init__(self, property1, property2, property3=None):
        self.property1 = property1
        self.property2 = property2
        self.property3 = property3

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "property1",
            ],
            "properties": [
                "property1": {
                    "type": "string"
                },
                "property2": {
                    "type": "string"
                },
                "property3": {
                    "type": "PropertySubclass"
                    "default": null
                }
            ]
        }
    }

# if you want to declare an list property, you can do it like this:
class Item:
    """
        @ptype property3: L{PropertySubclass}
        @ptype property4: C{list} of L{PropertySubclass}
    """
    def __init__(self, property1, property2, property3, property4=None):
        self.property1 = property1
        self.property2 = property2
        self.property3 = property3
        self.property4 = property4

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "property1",
            ],
            "properties": [
                "property1": {
                    "type": "string"
                },
                "property2": {
                    "type": "string"
                },
                "property3": {
                    "type": "PropertySubclass"
                    "default": null
                },
                "property4": {
                    "default": null,
                    "items": {
                        "type": "PropertySubclass"},
                        "type": "array"
                    }
                }
            ]
        }
    }

# if it is a query:
class ItemQueryHandler(GenericApiHandler):
    @swagger.operation(nickname='query')
    def get(self):
        """
           @param property1:
           @type property1: L{string}
           @in property1: query
           @required property1: False

           @param property2:
           @type property2: L{string}
           @in property2: query
           @required property2: True
           @rtype: L{Item}

           @notes: GET /item?property1=1&property2=1
        """

# Swagger json:
    "apis": [
        {
            "operations": [
                {
                    "parameters": [
                        {
                            "name": "property1",
                            "dataType": "string",
                            "paramType": "query",
                            "description": ""
                        },
                        {
                            "name": "property2",
                            "dataType": "string",
                            "paramType": "query",
                            "required": true,
                            "description": ""
                        }
                    ],
                    "responseClass": "Item",
                    "notes": null,
                    "responseMessages": [],
                    "summary": null,
                    "httpMethod": "GET",
                    "nickname": "query"
                }
            ],
            "path": "/item",
            "description": null
        },
        ....
    ]
```

# Running and testing

Now run your tornado app

```
python main.py
```

And visit:

```
curl http://ip:port/swagger/spec
```

access to web
```
http://ip:port/swagger/spec.html
```

# Passing more metadata to swagger
customized arguments used in creating the 'swagger.docs' object will be supported later
