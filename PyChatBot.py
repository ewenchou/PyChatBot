import json
from flask import Flask
from storage.Redis import RedisAdapter
from storage.Scheduler import Scheduler
from Router import Router
from flask_restful import Api
from collections import OrderedDict

Config = json.load(open('config/config.json'), object_pairs_hook=OrderedDict)
app = Flask(__name__, static_url_path=Config['static_path'])
storage = RedisAdapter(Config['redis_host'],Config['redis_port']).get_storage()
scheduler = Scheduler(Config['redis_host'], Config['redis_port'])
router = Router(storage)

api = Api(app)
#TODO we need to add some comments about this magic
for transport_to_init in Config['transports']:
    module = __import__('transport.' + transport_to_init)
    transport_class = getattr(getattr(module, transport_to_init), transport_to_init)
    transport_instance = transport_class(router, **Config['transports'][transport_to_init])
    module = __import__('transport.' + transport_to_init)
    end_point_name = transport_to_init + 'EndPoint'
    api_class = getattr(getattr(module, transport_to_init), end_point_name)

    for end_point in transport_instance.get_end_points_to_add():
        api.add_resource(api_class, transport_instance.access_point_root + end_point,
                         endpoint=transport_instance.access_point_root + end_point,
                         resource_class_kwargs={'transport': transport_instance, 'app': app})

if __name__ == '__main__':
    app.run(debug=True)
