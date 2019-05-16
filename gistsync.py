import requests
import json
import os

r = requests.get("https://api.github.com/users/rarecoil/gists")
gists = r.json()

for gist in gists:
    gist_path = os.path.join(os.path.dirname(__file__), "gists/", gist['id'])

    if not os.path.isdir(gist_path):
        os.mkdir(gist_path)

    for file_key in gist['files']:
        file = gist['files'][file_key]
        file_path = os.path.join(gist_path, file['filename'])
        file_req = requests.get(file['raw_url'])
        with open(file_path, 'w') as f:
            f.write(file_req.text)
