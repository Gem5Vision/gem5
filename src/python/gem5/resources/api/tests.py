from mongoclient import MongoClient
from jsonclient import JSONClient


resource_id = "x86-ubuntu-18.04-img"
version = "1.0.0"

mongo = MongoClient(
    "mongodb+srv://gem5_user:gem5_user@gem5-vision.wp3weei.mongodb.net/?retryWrites=true&w=majority",
    "gem5-vision",
    "resources")
# json = JSONClient("C:/Users/hello/Downloads/kiwi.json")

# print(json.get_resource_obj(resource_id))
# print(mongo.get_resource_obj(resource_id))
# jsonObj = json.get_resource_obj(resource_id, version)
mongoObj = mongo.get_resource_obj(resource_id, version)
# print(jsonObj)
print(mongoObj)
# print(jsonObj == mongoObj)
