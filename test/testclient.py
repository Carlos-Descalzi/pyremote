from pyremote import ObjectClient


test_object = ObjectClient('http://localhost:8080/test_object')

print(test_object.do_something('XXXX'))