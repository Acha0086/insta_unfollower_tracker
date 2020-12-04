""" Tracks who has unfollowed you on instagram since you last ran the script.
__author__ = Allan Chan
"""

from selenium import webdriver  # pip install selenium and webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import ctypes
import sys


def element_selector(browser, mode, path, multiple=False, func=None):
    """ Searches and returns an element on a specified path.
    :params:
        - browser: webdriver for chrome
        - mode: 'css' or 'xpath' depending on the path format
        - path: path of the element
        - multiple:
            - True: returns a list of elements on the path
            - False: returns a single element on the path
        - func: performs a given function
    """
    loaded = False
    while not loaded:
        try:
            if mode == 'css':
                if multiple is False:
                    element_selected = browser.find_element_by_css_selector(path)
                elif multiple is True:
                    element_selected = browser.find_elements_by_css_selector(path)
            elif mode == 'xpath':
                if multiple is False:
                    element_selected = browser.find_element_by_xpath(path)
                elif multiple is True:
                    element_selected = browser.find_elements_by_xpath(path)
            elif mode == 'class':
                if multiple is False:
                    element_selected = browser.find_element_by_class_name(path)
                elif multiple is True:
                    element_selected = browser.find_elements_by_class_name(path)
            if func is None:
                loaded = True
                return element_selected
            elif func(browser, mode, path):
                loaded = True
                return element_selected
        except Exception:
            pass


if __name__ == "__main__":
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # uncomment if you want to see browser
    chrome_options.add_argument("--window-size=1024,768")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    url = "https://www.instagram.com/[user]/followers"  # replace user with your profile
    browser.get(url)

    # read login details and sign in
    with open("login.txt") as f:
        lines = f.readlines()
        email = lines[0]
        password = lines[1]
    email_field = element_selector(browser, 'css', '#loginForm > div > div:nth-child(1) > div > label > input')
    email_field.send_keys(email)
    password_field = element_selector(browser, 'css', '#loginForm > div > div:nth-child(2) > div > label > input')
    password_field.send_keys(password)
    login_button = element_selector(browser, 'xpath', '//*[@id="loginForm"]/div/div[3]/button')
    login_button.click()

    # navigate to follower list
    not_now_button = element_selector(browser, 'xpath', '//*[@id="react-root"]/section/main/div/div/div/div/button')
    not_now_button.click()
    followers_element = element_selector(browser, 'xpath', '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
    followers_count = element_selector(browser, 'css', '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span')
    followers_count = int(followers_count.text)
    followers_element.click()
    followers_page = element_selector(browser, 'css', '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a')

    # scroll down all followers
    def last_follower(browser, mode, path):
        """ Scrolls until the last follower is loaded.

        :params:
            - browser: webdriver for chrome
            - mode: 'css' or 'xpath' depending on the path format
            - path: path of the element
        """
        all_elements = element_selector(browser, mode, path, multiple=True)
        last_element = all_elements[-1]
        while len(all_elements) != followers_count:
            browser.execute_script("arguments[0].scrollIntoView();", last_element)
            all_elements = element_selector(browser, mode, path, multiple=True)
            last_element = all_elements[-1]
        return True

    # add each follower to hash table
    current_follower_hash = {}

    def add_followers(browser, mode, path):
        follower_links = element_selector(browser, mode, path, multiple=True)
        for follower in follower_links:
            current_follower_hash[str(follower.get_attribute('href'))] = True
        if len(current_follower_hash) == followers_count:
            return True

    # find an element that contains an identifier to each follower
    element_selector(browser, 'css', 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li > div > div.Igw0E.IwRSH.eGOV_._4EzTm.yC0tu > div > div > a', multiple=True, func=add_followers)

    unfollower_hash = {}
    with open("followers.txt", "r+") as f:
        # checks if any previous followers are not currently followers
        lines = f.readlines()
        for follower in lines:
            follower = follower.rstrip("\n")
            if str(follower) not in current_follower_hash:
                unfollower_hash[follower] = True

        # writes all current followers to text file
        f.truncate(0)
        f.seek(0)
        for index, follower in enumerate(current_follower_hash):
            if index == len(current_follower_hash) - 1:
                f.write(follower)
            else:
                f.write(str(follower) + "\n")
        f.truncate()

    # writes unfollowers to a text file
    with open("unfollowers.txt", "a") as f:
        for unfollower in unfollower_hash:
            f.write(str(unfollower) + "\n")

    ctypes.windll.user32.MessageBoxExW(0, f"You have {len(unfollower_hash)} new unfollowers!", "Instagram unfollower tracker!", 0x40000)
    browser.quit()
    sys.exit()
