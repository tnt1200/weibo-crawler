#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# version 1.02
import re
import os
import sys
import time
import lxml
import pickle
import requests
import urlparse
from bs4 import BeautifulSoup
from misc import *


def main():
    from pprint import pprint
    robot = WeiboRobot('', '')  # username & password
    info = robot.get_user_info('')  # user id
    pprint(info)


class WeiboRobot(requests.Session):

    """weibo WeiboRobot class"""
    index_url = "http://weibo.cn"
    login_url = "http://login.weibo.cn/login/"
    # userinfo_urls
    username_url = "http://weibo.cn/%s?st=%s"
    follow_url = "http://weibo.cn/%s/follow?page=%d&st=%s"
    info_url = "http://weibo.cn/%s/info?st=%s"
    rank_url = "http://weibo.cn/%s/urank"
    at_url = "http://weibo.cn/at/weibo?uid=%s"
    search_url = "http://weibo.cn/search/mblog"
    search_params = {'hideSearchFrame': None,
                     'keyword': None, 'page': None, 'st': None}
    login_post = {'remember': 'on'}
    # operation
    attention_url = "http://weibo.cn/attention/add?uid=%s&rl=0&st=%s"
    # ???
    special_attention_url = "http://weibo.cn/attgroup/special?fuid=%s&st=%s"
    # cookie store
    cookie_dir = os.path.join(os.path.dirname(__file__), 'cookie/')
    cookie_ext = '.cookie'
    # sina ?st value
    st_value = ""
    headers_ua = {
        'User-Agent': 'LG-GC900/V10a Obigo/WAP2.0 Profile/MIDP-2.1 Configuration/CLDC-1.1'}

    visited_user = {}

    def __init__(self, username, password):
        requests.Session.__init__(self)
        self.username = username
        self.password = password
        self.headers = self.headers_ua
        self.login(self.username, self.password)
        self.init_st()  # init st token

    def init_st(self):
        req = self.get(self.index_url)
        soup = BeautifulSoup(req.text)
        parsed = self.parse_href(soup.form['action'])
        self.st_value = parsed.get('st')[0]

    def search_keyword(self, keywords, page):
        """return list of results"""
        params = self.search_params
        params['keyword'] = keywords
        params['st'] = self.st_value
        params['page'] = page
        req = self.get(self.search_url, params=self.search_params)
        if len(req.history) != 0:
            print 'sina weibo search limit reached'
            exit()
        soup = BeautifulSoup(req.text, 'lxml')
        result_list = []
        for tweet in soup.find_all('div', class_='c'):
            # div class=c
            if tweet.get('id'):
                if tweet.div.find('span', class_='cmt'):
                    pass
                else:
                    tweet_id = tweet.get('id')[2:]  # e.g. 'M_BcB181ToF'
                    tweet_screenid = tweet.div.a.string
                    tweet_userid = self.extract_userid(tweet.div.a['href'])
                    tweet_content = tweet.div.find(
                        'span', class_='ctt').__str__().lstrip(':')
                    result_list.append(
                        {'screenid': tweet_screenid, 'id': tweet_userid, 'tweetid': tweet_id, 'content': tweet_content})
        return result_list

    def login(self, username, password):
        cookie_file = self.cookie_dir + self.username + self.cookie_ext
        if os.path.isfile(cookie_file):
            with open(cookie_file) as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                self.cookies = cookies
        # todo
        # import md5 m=md5.new('username')
        # m.hexdigest()
        else:
            req = self.get(self.login_url)
            soup = BeautifulSoup(req.text, 'lxml')
            action = self.login_url + soup.form['action']
            # generate post data
            for tag in soup.form.find_all('input'):
                if tag['name'] == 'mobile':
                    self.login_post[tag['name']] = self.username
                elif 'password' in tag['name']:
                    self.login_post[tag['name']] = self.password
                elif tag['name'] != 'remember':
                    self.login_post[tag['name']] = tag['value']
            self.post(action, data=self.login_post)
            with open(cookie_file, 'w') as f:
                pickle.dump(
                    requests.utils.dict_from_cookiejar(self.cookies), f)

    def check_login(self):
        soup = BeautifulSoup(self.get(self.index_url).text)
        if u'\u6211\u7684\u9996\u9875' in soup.title:
            return True
        else:
            return False

    def get_user_info(self, numid):  # input numid!!
        sex = None
        name = None
        area = None
        birth = None
        brief = None
        rank = 0
        loginday = 0
        weibocount = 0
        fans = 0
        follow = 0
        info_url = self.info_url % (str(numid), self.st_value)
        urank_url = self.rank_url % str(numid)
        user_index_url = self.username_url % (str(numid), self.st_value)

        rank_page = self.get(urank_url).text
        index_page = self.get(user_index_url).text
        info_page = self.get(info_url).text
        # print info_text
        info_dict = {}
        try:
            rank = r_rank.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            sex = r_sex.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            name = r_name.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            area = r_area.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            birth = r_birth.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            brief = r_brief.search(info_page).group(1)
        except AttributeError:
            pass
        try:
            loginday = r_loginday.search(rank_page).group(1)
        except AttributeError:
            pass
        try:
            weibocount = r_weibocount.search(index_page).group(1)
        except AttributeError:
            pass
        try:
            fans = r_fans.search(index_page).group(1)
        except AttributeError:
            pass
        try:
            follow = r_follow.search(index_page).group(1)
        except AttributeError:
            pass
        info_dict = {'screenid': name, 'area':
                     area, 'sex': sex, 'birth': birth, 'rank': rank, 'brief': brief, 'loginday': loginday, 'weibocount': weibocount, 'fans': fans, 'follow': follow}
        return info_dict

    def id_to_numid(self, username):  # name modified
        try:
            return self.visited_user[username]
        except KeyError:
            req = self.get(self.username_url % (username, self.st_value))
            try:
                numid = r_numid.search(req.text).group(1)
            except AttributeError:
                numid = None
            return numid

    @staticmethod
    def extract_userid(url):
        match = r_userid.search(url)
        try:
            return match.group(1) or match.group(2)
        except AttributeError, e:
            print 'url error'
            return None

    @staticmethod
    def parse_href(query_str):
        query = urlparse.urlparse(query_str).query
        return urlparse.parse_qs(query)  # {'st':['aaaa']}

if __name__ == '__main__':
    main()
