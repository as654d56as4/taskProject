import uuid

def uid(string):
    data= '{}-{}'.format(str(uuid.uuid4()),string)
    return data