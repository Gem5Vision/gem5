from client_wrapper import get_resource_obj

resource_id = "x86-ubuntu-18.04-img"
version = "1.1.0"

print(get_resource_obj(resource_id, version))
print(get_resource_obj(resource_id, version, "atharav"))
