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

api = mcp.API()
api.DRIVER_PATH = "/home/akimosi/Documents/moneycontrolPy/chromedriver"

# user_url = "https://mmb.moneycontrol.com/arvind151-user-profile-617276696e64313531.html"

# user_info = api.get_user_info(
#     user_url,
#     save_as_json=True,
#     file_path="data/",
#     following_boarders_limit=50,
#     following_stocks_limit=50,
#     boarders_following_limit=50,
#     SCROLL_PAUSE_TIME=3
# )

top_boarders = api.get_top_boarders(
    save_as_json=True,
    file_path="/home/akimosi/Documents/moneycontrolPy/data",
    SCROLL_PAUSE_TIME=3,
)
# with open('/home/akimosi/Documents/moneycontrolPy/data/top_boarders.json','r') as top_boarders_file:
#     top_boarders = json.load(top_boarders_file)
# top_boarders_file.close()

boarders_url = list()
for boarder in top_boarders:
    boarders_url.append(boarder["boarder_url"])

with open(
    "/home/akimosi/Documents/moneycontrolPy/data/bundle.json", "r+"
) as details_file:
    bundle = json.load(details_file)

user_data = list()
user_data_existing_url = list()
for url in boarders_url:
    if url not in user_data_existing_url:
        user_data.append(api.get_user_info(url))
        user_data_existing_url.append(url)
        if len(user_data_existing_url) % 2 == 0:
            api.save_json(
                user_data,
                "user_data.json" + str(bundle["count"]),
                "/home/akimosi/Documents/moneycontrolPy/data/",
            )
            bundle["count"] += 1
            user_data = list()

# api.save_json(user_data,'user_data.json','/home/akimosi/Documents/moneycontrolPy/data/')
# api.save_json(user_data_existing_url, 'user_data_existing_url.json','/home/akimosi/Documents/moneycontrolPy/data/')

end_time = time.time()
print(f"Time Taken: {(end_time - start_time):.2f} sec")
