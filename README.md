# moneycontrolPy
Moneycontrol.com is an Indian online business news website owned by E-EIGHTEEN Dot Com Ltd., a subsidiary of the media house TV18. moneycontrolPy is a python API for [Money Control Forum]. 
## Features
  - Get User Information
  - Get Post Information
  - Get Stock Information
  - Get top boarders
  - Get stock in the news

## Dependencies
Before running the the package make sure you already have these pip packages.
* datetime
* json
* re
* time
* dateparser
* bs4
* selenium

and the same chromedriver version of your current Google Chrome Browser. You can download the respective chromedriver from [here]. 

### Installation
moneycontrolPy requires python3.6 and above to run. Install the dependencies and moneycontrolPy from pip.
```sh
pip install moneycontrolPy
```
## Documentation
After installing, you can import the package by
```py
import moneycontrolPy.mcp as mcp

api = mcp.API()
api.DRIVER_PATH = 'path_to_your_chromedriver_file/chromedriver'

url_user = "https://mmb.moneycontrol.com/arvind151-user-profile-617276696e64313531.html"
url_post = "https://mmb.moneycontrol.com/forum-topics/stocks/hero-motocorp/thread-message-81248383-83073237.html"
url_stock = 'https://mmb.moneycontrol.com/forum-topics/stocks/ab-money-246165.html'

"""
You could change the urls if you want to search 
for a specific user/post/stock from the moneycontol forum.
"""

user_info = api.get_user_info(url_user)                 #To extract the user information
post_info = api.get_post_info(url_post)                 #To extract the post information
stock_info = api.get_stock_info(url_stock)              #To extract the stock information
top_boarders = api.get_top_boarders()                   #To extract the top boarders
hot_stocks = api.get_stock_in_the_news()                #To extract the stock in the news

"""
There are numerous options/parameters available for each of the above functions functions. 
Please refer the docstring to find them all or you could see the source code & try to understand them.
All these functions returns a dict.
You can same them as json by passing the following parameter

Eg.

user_info = api.get_user_info(url_user,save_as_json=True)
"""
```
### Development

Want to contribute? Great! Find [moneycontrolPy Github repo] and feel free to fork and modify to your need.

### Todos

 - Better scrolling methods.
 - Code standardization.
 - Including other web browser drivers.

License
----

MIT




   [Money Control Forum]: <https://mmb.moneycontrol.com/>
   [here]: <https://chromedriver.chromium.org/downloads>
   [moneycontrolPy Github repo]: <https://github.com/AkiMosi/moneycontrolPy>