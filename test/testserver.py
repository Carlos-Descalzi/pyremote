from pyremote import ObjectServer

class TestObject:

    def do_something(self, param):
        return f'Hola!!!{param}'

server = ObjectServer()
server.add_object(TestObject(),'test_object')

server.run()