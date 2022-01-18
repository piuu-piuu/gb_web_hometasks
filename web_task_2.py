# X5Us6PgGYCE7hb1tJH6RdI5Z16u9LK49

import json
import requests


with open('responce_2.json', 'a', encoding="utf-8") as f:

    _keyword = 'python'

    params = {
        "q": _keyword,
        "api_key": "X5Us6PgGYCE7hb1tJH6RdI5Z16u9LK49",
        "limit": "1",
    }

    url = "http://api.giphy.com/v1/gifs/search"
    with requests.get(url, params=params) as response:
        data = response.json()

    main_data = {_keyword: {
        "url": data['data'][0]['url'],
        "title": data['data'][0]['title'],
        "source": data['data'][0]['source'],
        "type": data['data'][0]['type'],
        "rating": data['data'][0]['rating'],
        "import_datetime": data['data'][0]['import_datetime'],
        "size": [data['data'][0]['images']['original']['height'], data['data'][0]['images']['original']['width']]
    }}

    json.dump(main_data, f, indent=4)
