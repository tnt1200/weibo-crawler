#!/usr/bin/env python
# -*- coding: UTF-8 -*-

r_sex = re.compile(u'>性别:(.*?)<')
r_name = re.compile(u'>昵称:(.*?)<')
r_area = re.compile(u'>地区:(.*?)<')
r_brief = re.compile(u'>简介:(.*?)<')
r_birth = re.compile(u'>生日:(.*?)<')
r_loginday = re.compile(u'>微博等级：\d+级\((\d+)活跃天\)<')
r_renzheng = re.compile(u'>认证:(.*?)<')
r_rank = re.compile(u'urank">(\d+)级</a>')
r_userid = re.compile(u'http://weibo.cn/(\w{2,})|http://weibo.cn/u/(\w{2,})')
r_emotion = re.compile(u'\[.*?\]')
r_hashtag = re.compile(u'#.*?#')
r_url = re.compile(u'http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?')
r_weibocount = re.compile(u'>微博\[(\d+)\]<')
r_follow = re.compile(u'>关注\[(\d+)\]<')
r_fans = re.compile(u'>粉丝\[(\d+)\]<')
r_numid = re.compile(u'/(\d+)/follow')
r_online = re.compile(u'\[在线\]')


if __name__ == '__main__':
    pass
