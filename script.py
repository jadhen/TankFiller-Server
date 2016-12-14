from browser import document, alert, html, console,alert
def test():
    req = ajax.ajax()
    req.bind('complete',on_complete)
    # send a POST request to the url
    req.open('GET','127.0.0.1:5000',True)
    req.set_header('content-type','application/x-www-form-urlencoded')
    # send data as a dictionary
    req.send()
    return req.text

def test1():
    return "Hello world"

def test2():
    return "Hello world"

def on_complete(req):
   if req.status==200 or req.status==0:
       return req.text
