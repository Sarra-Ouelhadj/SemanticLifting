import requests

def insert(instance_path:str="./results/instances.ttl"):
    
    headers = {
        'Content-Type': 'application/x-turtle',
        'Accept': 'application/json'
    }

    with open(instance_path, 'rb') as f:
        requests.post('http://192.168.123.158:7200/repositories/Project/statements', data=f, headers=headers)
        # SPARQL Graph Protocol