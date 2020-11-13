import time
from flask import Flask
from flask_graphql import GraphQLView
from flask_sockets import Sockets
from graphql_ws.gevent import GeventSubscriptionServer

from models import db_session
from schema import schema

from time import time as timer
import json 

app = Flask(__name__)
app.debug = True
sockets = Sockets(app)


# class SomeMiddleware(object):
#     def resolve(self, next, root, info, **args):
#         next_node = next(root, info, **args)
#         if info:
#             print(dir(info))
#             print('info.context,',info.context)
#             print('info.field_asts,',info.field_asts)
#             print('info.field_name,',info.field_name)
#             print('info.fragments,',info.fragments)
#             print('info.operation,',info.operation)
#             print('info.parent_type,',info.parent_type)
#             print('info.path,',info.path) # info.path, ['addTodo']
#             print('info.return_type,',info.return_type) 
#             print('info.root_value,',info.root_value)
#             # print('info.schema,',info.schema)
#             # print('info.variable_values,',info.variable_values)
#         return next_node

# dummy_middleware = SomeMiddleware()

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True, # for having the GraphiQL interface
        # middleware=[dummy_middleware]
    )
)




subscription_server = GeventSubscriptionServer(schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'

@sockets.route('/subscriptions')
def echo_socket(ws):
    subscription_server.handle(ws)
    return []

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
