import requests
import json

user = 'sigma67'
uri = f'https://api.github.com/users/{user}/repos'

r = requests.get(uri).json()
with open('responce.json', 'w', encoding='utf-8') as f:
    json.dump(r, f, indent=4)
