#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 12:03:57 2020

@author: akimosi
"""


from moneycontrolPy import mcp
import time
import json

start_time = time.time()

root_dir = "/home/akimosi/Documents/moneycontrolPy/"
bundle_size = 10

api = mcp.API()
api.DRIVER_PATH = root_dir + "chromedriver"

top_boarders = api.get_top_boarders(
    save_as_json=True, file_path=root_dir + "data/", SCROLL_PAUSE_TIME=3,
)

with open(root_dir + "data/top_boarders.json", "r") as top_boarders_file:
    top_boarders = json.load(top_boarders_file)
top_boarders_file.close()

boarders_url = list()
for boarder in top_boarders:
    boarders_url.append(boarder["boarder_url"])

with open(root_dir + "data/bundle.json", "r+") as details_file:
    bundle = json.load(details_file)

user_data = list()
user_data_existing_url = list()
csv_file = open('existing_user_url.csv','a')
for url in boarders_url:
    if url not in user_data_existing_url:
        user_data.append(api.get_user_info(url))
        user_data_existing_url.append(url)
        if len(user_data_existing_url) % bundle_size == 0:
            api.save_json(
                user_data, "user_data.json" + str(bundle["count"]), root_dir + "data/",
            )
            bundle["count"] += 1
            api.save_json(bundle, "bundle.json", "data/")
            csv_file.write(url)
            user_data = list()
            

api.save_json(
    user_data, "user_data.json", root_dir + "data/"
)


end_time = time.time()
print(f"Time Taken: {(end_time - start_time):.2f} sec")
