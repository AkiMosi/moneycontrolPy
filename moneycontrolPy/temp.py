# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 12:03:57 2020

@author: akimosi
"""


import mcp
import time

start_time = time.time()

api = mcp.API()
api.DRIVER_PATH = '/home/akimosi/Documents/moneycontrolPy/chromedriver'

user_url = 'https://mmb.moneycontrol.com/arvind151-user-profile-617276696e64313531.html'

user_info = api.get_user_info(
    user_url,
    # save_as_json=True,
    # file_path="",
    following_boarders_limit=50,
    following_stocks_limit=50,
    boarders_following_limit=50,
    post_limit=20,
    SCROLL_PAUSE_TIME=5
)

end_time = time.time()
print(f'Time Taken: {(end_time - start_time):.2f} sec')