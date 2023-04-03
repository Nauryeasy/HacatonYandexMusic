global_storage = {}


def set_key(global_storage, key, value):
    global_storage[key] = value


def get_key(global_storage, key):
    return global_storage[key]


def delete_key(global_storage, key):
    global_storage.pop(key)