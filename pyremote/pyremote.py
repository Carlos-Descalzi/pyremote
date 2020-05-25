import flask
import inspect
import requests
import pickle
import io
import base64

class ObjectServer:
    """
    Object server, exposes objects as HTTP endpoints.
    """
    def __init__(self, host='0.0.0.0',port=8080, prefix=''):
        """
        params:
            host: Listener host name, optional, default 0.0.0.0.
            port: Optional, default 8080.
            prefix: Path prefix, default ''
        """
        self._host = host
        self._port = port
        self._app = flask.Flask(__name__)
        self._prefix = prefix

    def add_object(self, obj, name=None):
        """
        Adds an object, creating endpoints for its public methods.
        params:
            obj: The instance being exposed.
            name: Optional, defaults to class name.
        """
        obj_name = name or obj.__class__.__name__

        methods = self._get_methods(obj)

        for method_name, method in methods:
            path = f'{obj_name}/{method_name}'
            self._app.add_url_rule(
                f'{self._prefix}/{path}', 
                path, 
                MethodWrapper(obj,method),
                methods=['POST']
            )

    def _get_methods(self, obj):

        obj_class = obj.__class__

        result = []
        for item in dir(obj_class):
            item_val = getattr(obj_class,item)
            
            if inspect.isfunction(item_val) and item[0] != '_':
                result.append((item, item_val))
        return result

    def run(self):
        """
        Application main loop.
        """
        self._app.run(threaded=True, host=self._host, port=self._port)

    def get_app(self):
        """
        Returns the application, to be used by other services like uwsgi.
        """
        return self._app


class ObjectClient:
    """
    Client proxy. This object will expose methods as defined on server side.
    """
    def __init__(self, url):
        """
        Params:
            url: The url of the object on server side.
        """
        self._url = url

    def __getattr__(self, name):
        
        if name != '_url':
            return MethodProxy(f'{self._url}/{name}')
        
        raise AttributeError(name)

class MethodWrapper:
    def __init__(self, obj, method):
        self._obj = obj
        self._method = method

    def __call__(self):

        args, kwargs = self._parse_request()

        return self._encode_return(self._method(self._obj,*args,**kwargs))

    def _parse_request(self):

        data = base64.b64decode(flask.request.data)

        args, kwargs = pickle.loads(data)

        return args, kwargs

    def _encode_return(self, data):
        return base64.b64encode(pickle.dumps(data))

class MethodProxy:

    def __init__(self, url):
        self._url = url

    def __call__(self, *args, **kwargs):
        
        payload = (args, kwargs)

        content = pickle.dumps(payload)

        data = base64.b64encode(content)

        r = requests.post(self._url,data=data)

        if r.status_code != 200:
            raise Exception(r.text)

        return pickle.loads(base64.b64decode(r.text))



