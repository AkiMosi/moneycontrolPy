import datetime
import json
import re
from time import sleep

import dateparser
from bs4 import BeautifulSoup
from selenium import webdriver

# from tqdm import tqdm


class API:
    def __init__(self):
        """
        The constructor of the class API.
        There are three class members, HOME_PAGE, TOP_BOARDERS_URL, and DRIVER_PATH.
        The DRIVER_PATH is initialized with ''. The proper DRIVER_PATH must be set, before using any of the function.
        And currently, use the latest chromedriver.

        Returns
        -------
        None.

        """

        self.HOME_PAGE = "https://mmb.moneycontrol.com"
        self.TOP_BOARDERS_URL = "https://mmb.moneycontrol.com/top-boarders/"
        self.DRIVER_PATH = ""

    def _init_driver(self, WEB_DRIVER_PATH):
        """
        This method is to initialize the driver. A new driver is initialized for all methods.        
        There are some default options given to the driver, to make it ignore some certificate errors,
        that is to ignore the pop up box which comes when we use an uncertified webpage. And the driver is made a headless, so that it could be faster.
        This method is only invoked by the _parse().

        Parameters
        ----------
        WEB_DRIVER_PATH : TYPE string
            DESCRIPTION. Path of the chromedriver.

        Returns
        -------
        driver : TYPE selenium.webdriver.chrome.webdriver.WebDriver
            DESCRIPTION. driver to get the source code of the webpage.

        """

        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        # options.add_argument("--headless")
        driver = webdriver.Chrome(WEB_DRIVER_PATH, options=options)

        return driver

    def _parse(self, url, SCROLL_PAUSE_TIME=None, limit=None, limit_query=None):
        """
        This method invokes the _inti_driver and gets the HTML sourse of the page. Using Beautiful Soup the HTML is parsed and returned.
        If the default SCROLL_PAUSE_TIME is None, if then then page won't get scrolled. In some cases, the contents are loaded only when the page is loaded, then the SCROLL_PAUSE_TIME should be given some floating point value.
        The limit is to limit the number of return object, because some of the methods couold lead to the web page, where it is like an infinite scroll, so to save time, limit is given. 
        The limit query is implicitly generatd for all the methods, which could give limit.

        Parameters
        ----------
        url : TYPE string
            DESCRIPTION. web link of the user

        SCROLL_PAUSE_TIME : TYPE float
            DESCRIPTION. To wait for the driver to load the page.

        Returns
        -------
        soup : TYPE bs4.BeautifulSoup
            DESCRIPTION. BeautifulSoup to parse the html

        """
        driver = self._init_driver(self.DRIVER_PATH)
        driver.implicitly_wait(SCROLL_PAUSE_TIME)
        driver.get(url)

        if SCROLL_PAUSE_TIME or limit is not None:
            if SCROLL_PAUSE_TIME is None:
                SCROLL_PAUSE_TIME = 1
            soup = self._scroll_page(
                driver,
                SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
                limit=limit,
                limit_query=limit_query,
            )
            if limit and soup is not None:
                return soup
        html = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        )
        soup = BeautifulSoup(html, features="lxml")
        driver.close()

        return soup

    def _scroll_page(self, driver, SCROLL_PAUSE_TIME, limit=None, limit_query=None):
        """
        To scroll the browser until the end of the webpage. When the SCROLL_PAUSE_TIME is None, the page is left unscrolled.
        And if the limit is not None, even if the SCROLL_PAUSE_TIME is none, it is set to 1, to scroll through pages. If we got enough data that to meet up the limit, the method breaks.

        Parameters
        ----------
        driver : TYPE elenium.webdriver.chrome.webdriver.WebDriver
            DESCRIPTION. driver to get the source code of the webpage.

        SCROLL_PAUSE_TIME : TYPE float
            DESCRIPTION. To wait for the driver to load the page.

        Returns
        -------
        None.

        """

        last_height = driver.execute_script("return document.body.scrollHeight")
        sleep(SCROLL_PAUSE_TIME)
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(SCROLL_PAUSE_TIME)
            if limit is not None:
                html = driver.execute_script(
                    "return document.getElementsByTagName('html')[0].innerHTML"
                )
                soup = BeautifulSoup(html, "lxml")
                division = soup.find(
                    limit_query[0]["search"], class_=limit_query[0]["class"]
                )

                if (
                    len(
                        division.findAll(
                            limit_query[1]["search"], class_=limit_query[0]["class"]
                        )
                    )
                    >= limit
                ):
                    return soup
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _extract_following_stocks(self, soup, limit=None):
        """
        This method is used to get following_stocks. This method return a list of dictionaries, having the following keys.

        stock_name      : The name of the stock

        stock_url       : The detailed view of the stock, from which we can get the stock info. 
                          NOTE: The method get_stock_info() should use the url generated by this method.

        opinion         : Number of opinions about the stock

        no_followers    : Number of followers of the stock

        Parameters
        ----------
        soup : TYPE TYPE bs4.BeautifulSoup
            DESCRIPTION. BeautifulSoup to parse the html

        Returns
        -------
        to_return : TYPE list 
            DESCRIPTION. list of following stock with their respective URL of the detailed view

        """
        to_return = list()

        division = soup.find("div", class_="clearfix ptf20")
        if division is not None:
            name = division.findAll("a", class_="txt18gry", limit=limit)
            url = division.findAll("a", class_="anchbtmde", limit=limit)
            opinion = list()
            for i in division.findAll("p", class_="wpost_opnions MT3", limit=limit):
                if (i.span.getText().strip()).isdigit():
                    opinion.append(int(i.span.getText().strip()))
                else:
                    opinion.append(None)

            no_followers = list()
            for i in division.findAll("div", class_="MT5 anchmsg2 ML5", limit=limit):
                if (i.span.getText().strip()).isdigit():
                    no_followers.append(int(i.span.getText().strip()))
                else:
                    no_followers.append(None)

            for i, j, k, l in zip(name, url, opinion, no_followers):
                stock = dict(
                    {
                        "stock_name": i.getText().strip(),
                        "stock_url": j["href"],
                        "opinion": k,
                        "no_followers": l,
                    }
                )
                to_return.append(stock)

        return to_return

    def _extract_info(self, soup, search_name, class_name, key, limit=None):
        """
        This method is used to fetch the details like following_topics, following_boarders, boarders_following.
        The return object has mostly the name, url, no_followers and opinion or no_messages.

        Parameters
        ----------
        soup : TYPE bs4.BeautifulSoup
            DESCRIPTION. BeautifulSoup to parse the html
        search_name : TYPE list of string(2)
            DESCRIPTION. A list of search names for the soup.find function.
        class_name : TYPE list of string(4)
            DESCRIPTION. A lsit of string for the class_ attribute of the soup.find function.
        key : TYPE List of strings(4)
            DESCRIPTION. A list of key names of the returning dictionary object.

        Returns
        -------
        to_return : TYPE list
            DESCRIPTION. list of all the information

        """
        to_return = list()

        division = soup.find("div", class_=class_name[0])
        if division is not None:
            name = division.findAll("a", class_=class_name[1], limit=limit)
            num = list()
            for i in division.findAll(
                search_name[0], class_=class_name[2], limit=limit
            ):
                if i.span.getText().strip().isdigit():
                    num.append(int(i.span.getText().strip()))
                else:
                    num.append(None)

            no_fol = list()
            for i in division.findAll(
                search_name[1], class_=class_name[3], limit=limit
            ):
                if (i.span.getText().strip()).isdigit():
                    no_fol.append(int(i.span.getText().strip()))
                else:
                    no_fol.append(None)

            for i, j, k in zip(name, num, no_fol):
                to_return.append(
                    dict(
                        {
                            key[0]: i.getText().strip(),
                            key[1]: self.HOME_PAGE + i["href"],
                            key[2]: j,
                            key[3]: k,
                        }
                    )
                )

        return to_return

    def _extract_user_details(self, soup):
        """
        This method is to get the user details like, username, date_joined, reward_points and featured_stock, which is the topic, the user mostly writes about.

        Parameters
        ----------
        soup : TYPE bs4.BeautifulSoup
            DESCRIPTION. BeautifulSoup to parse the html

        Returns
        -------
        to_return : TYPE dict
            DESCRIPTION. A dictionary which contains the information about the user

        """

        to_return = dict(
            {"user_name": soup.find("span", class_="bfname FL").get_text().strip()}
        )
        data = list()
        featured_stock = list()
        values = soup.findAll("a", class_="flw_link")
        to_return["no_posts"] = int(values.pop(0).getText().split()[1])
        keys = [
            "no_following_stocks",
            "no_following_topics",
            "no_following_boarders",
            "no_boarders_following",
        ]

        for i, j in zip(keys, values):
            to_return[i] = int(j.getText().split()[2])

        ul = soup.find("ul", class_="blul")
        for i in ul.findChildren("li", recursive=False):
            data.append(i.getText())
        data = [re.split(" Member Since | Reward Point", str(i)) for i in data]
        to_return.update(
            {
                "date_joined": (dateparser.parse(data[0][1])).__str__(),
                "reward_points": int(data[1][1]),
            }
        )

        feat_stk = soup.find("div", class_="anchbtmde brd_br FL PR10")
        if feat_stk is not None:

            feat_stk_url = feat_stk.findAll("a")
            for j, i in zip(
                feat_stk_url,
                feat_stk.getText().replace("Mostly writes on ", "").split(","),
            ):
                featured_stock.append(
                    dict({"stock": i, "stock_url": self.HOME_PAGE + j["href"]})
                )
        to_return.update({"featured_stock": featured_stock})

        return to_return

    def _extract_post_details(self, soup, limit=None):
        """


        Parameters
        ----------
        soup : TYPE bs4.BeautifulSoup
            DESCRIPTION. BeautifulSoup to parse the html

        Returns
        -------
        to_return : TYPE list
            DESCRIPTION. List of details about the post

        """
        to_return = list()

        division = soup.find("ul", class_="clearfix follow_mainlist")
        if division is not None:
            text_url = division.find_all("a", class_="txt16gry", limit=limit)
            post_time = division.findAll("div", class_="link13gry", limit=limit)
            for i, j in zip(text_url, post_time):
                p_time = j.getText().strip()
                try:
                    p_time_yr = p_time + " " + str(datetime.datetime.today().year)
                    time_obj = datetime.datetime.strptime(
                        p_time_yr, "%I.%M %p %b %dth %Y"
                    )
                except ValueError:
                    time_obj = dateparser.parse(p_time)
                post = {
                    "post_url": self.HOME_PAGE + i["href"],
                    "post_content": i.getText().strip(),
                    "posted_time": time_obj.__str__(),
                }
                to_return.append(post)

        return to_return

    def save_json(self, content, file_name, file_path=""):
        """


        Parameters
        ----------
        content : TYPE
            DESCRIPTION.
        file_name : TYPE
            DESCRIPTION.
        file_path : TYPE, optional
            DESCRIPTION. The default is ''.

        Returns
        -------
        None.

        """

        with open(file_path + file_name, "w") as fp:
            json.dump(content, fp, indent=4)

    def get_user_info(
        self,
        url,
        save_as_json=False,
        file_path="",
        SCROLL_PAUSE_TIME=1,
        following_stocks_limit=None,
        following_topics_limit=None,
        following_boarders_limit=None,
        boarders_following_limit=None,
        post_limit=None,
        limit_query=None,
    ):
        """
        This method is to get the complete details about the user. We could save the output of this method which is the lsit of dict in the form of JSON file, if the save_as_json is given as True. By default the the JSON file is stored in the directory where the program runs. It can be changed by giving the file_path.
        We can limit the number of following stocks, following topics, following boarders and following boarders. The limits are the maximum limit that can be returned. It doesn't mean that we wil get that much objects. It depends upon the network conectivity.


        Parameters
        ----------
        url : TYPE string
            DESCRIPTION. URL of the user
            EX: https://mmb.moneycontrol.com/arvind151-user-profile-617276696e64313531.html
        save_as_json : TYPE, optional
            DESCRIPTION. The default is False. The default is False. It is used to store the return object as a json file.
        file_path : TYPE string, optional
            DESCRIPTION. The default is "".The default is "". It mentions where the JSON file should be stored.
        SCROLL_PAUSE_TIME : TYPE float, optional
            DESCRIPTION. The default is 1. The default value is 1. To wait for the driver to load the page.
        following_stocks_limit : TYPE integer, optional
            DESCRIPTION. The default is None. To limit the details of following stock.
        following_topics_limit : TYPE ineteger, optional
            DESCRIPTION. The default is None. To limit the details of following topics.
        following_boarders_limit : TYPE integer, optional
            DESCRIPTION. The default is None. To limit the details of following boarders.
        boarders_following_limit : TYPE integer, optional
            DESCRIPTION. The default is None. To limit the details of boarders following. 
        post_limit : TYPE integer, optional
            DESCRIPTION. The default is None. To limit the details of post limit.
        limit_query : TYPE list of dict, optional
            DESCRIPTION. The default is None. The constraint to be checked when the limit is given. 
            This is not needed to give explicitly.
            It is addressed implicitly for all the functions.

        Returns
        -------
        to_return : TYPE dict
            DESCRIPTION. returns the details about the user

        """
        to_return = dict({"url": url})

        if url == "https://mmb.moneycontrol.com/follower-boarders/undefined":
            return to_return

        if post_limit is not None:
            limit_query = [
                {"search": "ul", "class": "clearfix follow_mainlist"},
                {"search": "a", "class": "txt16gry"},
            ]

        soup_main = self._parse(
            url,
            SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
            limit=post_limit,
            limit_query=limit_query,
        )

        user_details = self._extract_user_details(soup_main)

        to_return.update(
            {
                "user_name": user_details["user_name"],
                "date_joined": user_details["date_joined"],
                "reward_points": user_details["reward_points"],
                "no_posts": user_details["no_posts"],
                "no_following_stocks": user_details["no_following_stocks"],
                "no_following_topics": user_details["no_following_topics"],
                "no_following_boarders": user_details["no_following_boarders"],
                "no_boarders_following": user_details["no_boarders_following"],
                "featured_stocks": user_details["featured_stock"],
            }
        )

        post_details = list()
        if user_details["no_posts"] > 0:
            post_details = self._extract_post_details(soup_main, post_limit)
        to_return.update({"posts": post_details})

        link = soup_main.findAll("a", class_="flw_link")

        following_stocks = list()
        if user_details["no_following_stocks"] > 0:

            if following_stocks_limit is not None:
                limit_query = [
                    {"search": "div", "class": "clearfix ptf20"},
                    {"search": "a", "class": "txt18gry"},
                ]

            soup_following_stock = self._parse(
                link[1]["href"],
                SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
                limit=following_stocks_limit,
                limit_query=limit_query,
            )
            following_stocks = self._extract_following_stocks(
                soup_following_stock, following_stocks_limit
            )
        to_return.update({"following_stocks": following_stocks})

        following_topics = list()
        if user_details["no_following_topics"] > 0:

            if following_topics_limit is not None:
                limit_query = [
                    {"search": "div", "class": "clearfix ptf20"},
                    {"search": "a", "class": "txt18gry"},
                ]

            soup_following_topics = self._parse(
                link[2]["href"],
                SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
                limit=following_topics_limit,
                limit_query=limit_query,
            )
            following_topics = self._extract_info(
                soup_following_topics,
                ["div", "div"],
                ["clearfix ptf20", "txt18gry", "wpost_opnions", "MT5 anchmsg2 ML5"],
                ["topic_name", "topic_url", "opinion", "no_followers"],
                following_topics_limit,
            )
        to_return.update({"following_topics": following_topics})

        following_boarders = list()
        if user_details["no_following_boarders"] > 0:

            if following_boarders_limit is not None:
                limit_query = [
                    {"search": "div", "class": "clearfix PA15"},
                    {"search": "a", "class": "ancor12"},
                ]

            soup_following_boarders = self._parse(
                link[3]["href"],
                SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
                limit=following_boarders_limit,
                limit_query=limit_query,
            )
            following_boarders = self._extract_info(
                soup_following_boarders,
                ["p", "div"],
                ["clearfix PA15", "ancor12", "anchmsg MT3", "MT5 anchmsg ML5"],
                ["boarder_name", "boarder_url", "no_messages", "no_followers"],
                following_boarders_limit,
            )
        to_return.update({"following_boarders": following_boarders})

        boarders_following = list()
        if user_details["no_boarders_following"] > 0:

            if boarders_following_limit is not None:
                limit_query = [
                    {"search": "div", "class": "clearfix PA15"},
                    {"search": "a", "class": "ancor12"},
                ]

            soup_boarders_following = self._parse(
                link[4]["href"],
                SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
                limit=boarders_following_limit,
                limit_query=limit_query,
            )
            boarders_following = self._extract_info(
                soup_boarders_following,
                ["p", "div"],
                ["clearfix PA15", "ancor12", "anchmsg MT3", "MT5 anchmsg ML5"],
                ["boarder_name", "boarder_url", "no_messages", "no_followers"],
                boarders_following_limit,
            )
        to_return.update({"boarders_following": boarders_following})

        if save_as_json == True:
            self.save_json(to_return, "user_info.json", file_path)

        return to_return

    def get_post_info(self, url, save_as_json=False, file_path="", SCROLL_PAUSE_TIME=1):
        """
        This method is to get the data about a post, when it's url is given.

        Parameters
        ----------
        url : TYPE string
              EX: 'https://mmb.moneycontrol.com/forum-topics/stocks/hero-motocorp/thread-message-81248383-83073237.html'
            DESCRIPTION. URL of the post

        save_as_json : TYPE bool, optional
            DESCRIPTION. The default is False. It is used to store the return object as a json file.

        file_path : TYPE string, optional
            DESCRIPTION. The default is "". It mentions where the JSON file should be stored.

        SCROLL_PAUSE_TIME : TYPE float
            DESCRIPTION. The default value is 1. To wait for the driver to load the page.

        Returns
        -------
        to_return : TYPE dict
            DESCRIPTION. Returns the information about the post

        """
        to_return = dict()

        soup = self._parse(url, SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME)
        soup_box = soup.find("div", class_="clearfix lhtbg")

        temp = soup.find("span", class_="blu16_head").getText()
        no_replies = list((map(int, re.findall(r"\d+", temp))))[0]

        texts = soup.findAll("p", class_="txt16gry")
        post_text = texts.pop(0).getText().strip()
        user_url = soup_box.findAll("a", class_="txtnm14")

        replies = list()
        if no_replies > 0:
            for i, j in zip(texts, user_url[1::2]):
                reply = dict(
                    {
                        "text": i.getText().strip(),
                        "user_url": self.HOME_PAGE + j["href"],
                    }
                )
                replies.append(reply)

        to_return = {
            "post_text": post_text,
            "no_replies": no_replies,
            "replies": replies,
        }

        if save_as_json == True:
            self.save_json(to_return, "post_info.json", file_path)

        return to_return

    def get_stock_info(self, url, save_as_json=False, file_path=""):
        """
        This method gets the BSE and NSE values and percentage when the stock_url is given.

        Parameters
        ----------
        url : TYPE string
            DESCRIPTION. URL of the detailed view of the stock page.


        save_as_json : TYPE bool, optional
            DESCRIPTION. The default is False. It is used to store the return object as a json file.

        file_path : TYPE string, optional
            DESCRIPTION. The default is "". It mentions where the JSON file should be stored.

        Returns
        -------
        to_return : TYPE dict
            DESCRIPTION. Returns the information about the stock

        """
        to_return = dict()

        soup = self._parse(url, 0)
        class_name = [
            "span_price_wrap stprh grnclr",
            "span_price_wrap stprh grn_hilight grnclr",
            "span_price_wrap stprh rdclr",
            "span_price_wrap stprh red_hilight rdclr",
        ]

        for i in class_name:
            values = soup.find_all("span", class_=i)
            if values != []:
                break

        values = [float(i.getText().strip()) for i in values]
        temp = [i.getText().strip() for i in soup.findAll("em", limit=2)]
        perc = [float(re.findall(r"\d+\.*\d*", i)[0]) for i in temp]

        to_return = {
            "bse_value": values[0],
            "bse_percent": perc[0],
            "nse_value": values[1],
            "nse_percent": perc[1],
            "time_stamp": datetime.datetime.now().__str__(),
        }

        if save_as_json == True:
            self.save_json(to_return, "stock_info.json", file_path)

        return to_return

    def get_top_boarders(
        self,
        limit=10,
        limit_query=None,
        SCROLL_PAUSE_TIME=None,
        save_as_json=False,
        file_path="",
    ):
        """
        This method gets the top boarders.

        Parameters
        ----------
        limit : TYPE integer, optional
            DESCRIPTION. The default is 10. To limit the number of top boarders.
        limit_query : TYPE list of dict, optional
            DESCRIPTION. The default is None. This is the constraint that to be checked when the limit is used. This is done implicitly. Not needed to pass this explicitly.
        SCROLL_PAUSE_TIME : TYPE float, optional
            DESCRIPTION. The default is None. The time to wait for the driver to load the page while scrolling.
        save_as_json : TYPE boolean, optional
            DESCRIPTION. The default is False. To store the resulting list of dict as json.
        file_path : TYPE string, optional
            DESCRIPTION. The default is "". To specify where the JSON file should be stored.

        Returns
        -------
        to_return : TYPE list of dict.
            DESCRIPTION. The details about the top boarders.

        """

        to_return = list()

        if limit is not None:
            limit_query = [
                {"search": "div", "class": "PA20"},
                {"search": "a", "class": "ancor12a"},
            ]

        soup = self._parse(
            self.TOP_BOARDERS_URL,
            limit=limit,
            limit_query=limit_query,
            SCROLL_PAUSE_TIME=SCROLL_PAUSE_TIME,
        )
        division = soup.find("div", class_="PA20")
        name_url = division.findAll("a", class_="ancor12a", limit=limit)
        membership = [
            i.getText().strip()
            for i in division.findAll("p", class_="ancorou12 MT2", limit=limit)
        ]
        if limit is None:
            limit = 0
        temp = [i for i in division.findAll("p", class_="anchmsg MT3", limit=limit * 4)]
        total_msg = [int(i.span.getText().strip()) for i in temp[0::4]]
        msg_last_week = [int(i.span.getText().strip()) for i in temp[1::4]]
        msg_last_month = [int(i.span.getText().strip()) for i in temp[2::4]]
        followers = [int(i.span.getText().strip()) for i in temp[3::4]]

        for a, b, c, d, e, f in zip(
            name_url, membership, total_msg, msg_last_week, msg_last_month, followers,
        ):
            to_return.append(
                dict(
                    {
                        "boarder_name": a.getText().strip(),
                        "boarder_url": self.HOME_PAGE + a["href"],
                        "membership": b,
                        "total_messages": c,
                        "messages_last_week": d,
                        "messages_last_month": e,
                        "no_followers": f,
                    }
                )
            )

        if save_as_json == True:
            self.save_json(to_return, "top_boarders.json", file_path)

        return to_return

    def get_stock_in_the_news(self, save_as_json=False, file_path=""):
        """
        This method gets the stock in the news.        

        Parameters
        ----------
        save_as_json : TYPE boolean, optional
            DESCRIPTION. The default is False. To store the resulting list of dict as json.
        file_path : TYPE string, optional
            DESCRIPTION. The default is "".  To specify where the JSON file should be stored.

        Returns
        -------
        stocks : TYPE list of dict
            DESCRIPTION. The dict contains the name and the URL of the detailed view of the stock.

        """
        to_return = list()

        soup = self._parse(self.HOME_PAGE)
        division = soup.find("div", class_="anchlft auto_width nobor clearfix")

        for i in division.findAll("a"):

            name = i.getText().strip()
            soup_ = self._parse(self.HOME_PAGE + i["href"])
            url_ = soup_.find("a", class_="op_bl13")["href"]

            to_return.append(dict({"stock_name": name, "stock_url": url_}))

        if save_as_json == True:
            self.save_json(to_return, "stock_news.json", file_path)

        return to_return
