# pyremote
A very rustic way to do remoting object invocation call via HTTP.

## Sample of use

```python
# Server side
class TestObject:

    def do_something(self, param):
        return f'Hola!!!{param}'

server = ObjectServer()
server.add_object(TestObject(),'test_object')
server.run()


# Client side
test_object = ObjectClient('http://localhost:8080/test_object')
print(test_object.do_something('XXXX'))

```
