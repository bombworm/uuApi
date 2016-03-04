# -*- coding: utf-8 -*-
import time
import urllib
import urllib2
import re
import md5
import requests
import os

import logging

class uuApi():
    soft_id = ''
    soft_key = ''
    user_name = ''
    user_password = ''
    mac_address = ''
    uu_version = ''
    timeout = 60000
    uid = ''
    user_key = ''
    soft_content_key = ''
    server_mapping = None

    def __init__(self, soft_id, soft_key, user_name, user_password, mac_address='0011223344', uu_version='1.0.0.0', timeout=60000):
    	self.soft_id = soft_id
    	self.soft_key = soft_key
    	self.user_name = user_name
    	self.user_password = user_password
    	self.mac_address = mac_address
    	self.uu_version = uu_version
    	self.timeout = timeout
        self.user_login()

    def enable(self):
    	return self.uid != ''

    def get_server_url(self, server):
        if not self.server_mapping:
            url = "http://common.taskok.com:9000/Service/ServerConfig.aspx"
            res = urllib2.urlopen(url)
            text = res.read()
            ma = re.findall("\,(.*?)\:101\,(.*?)\:102\,(.*?)\:103", text)
            self.server_mapping = ma
        mapping = {"service" : 0, "upload": 1, "code": 2}
        if server in mapping.keys():
            return self.server_mapping[0][mapping[server]]

    def user_login(self):
        url = "http://%s%s" % (self.get_server_url('service'), '/Upload/Login.aspx' )
        hash = md5.new()
        hash.update(self.user_password)
        password = hash.hexdigest()
        getParam = {
            'U' : self.user_name, 
            'P' : password,
            'R' : int(time.time())
        }
        param = urllib.urlencode(getParam)
        res = urllib2.urlopen("%s?%s" % (url, param));
        result = res.read()
        if result:
            self.user_key = result
            token = result.split("_")
            self.uid =token[0]
            tmp = self.user_key + self.soft_id + self.soft_key
            hash = md5.new()
            hash.update(tmp.lower())
            self.soft_content_key = hash.hexdigest()
            return self.uid
        print "Login fail."
        return 

    def upload(self, image_path, code_type, auth):
        of = open(image_path, 'rb')
        files = {
            'img' : of
        }
        data = {
            'key' : self.user_key,
            'sid' : self.soft_id,
            'skey' : self.soft_content_key,
            'TimeOut' : self.timeout,
            'Type' : code_type,
        }

        if auth:
            data['Version'] = '100'

        url = "http://%s%s" % (self.get_server_url('upload'), '/Upload/Processing.aspx?R='+str(int(time.time())) )
        res = requests.post(url ,data=data,files=files) #proxies=proxies
        result = res.text
        return result

    def get_result(self, code_id):

        url = "http://%s%s" % (self.get_server_url('code'), '/Upload/GetResult.aspx' )
        hash = md5.new()
        hash.update(self.user_password)
        password = hash.hexdigest()
        getParam = {
            'KEY' : self.user_key, 
            'ID' : code_id,
            'Random' : int(time.time())
        }
        result = '-3'
        count = 120 #try times
        param = urllib.urlencode(getParam)
        apiUrl = "%s?%s" % (url, param)
        res = urllib2.urlopen(apiUrl);
        result = res.read()
        while result == '-3' and count > 0:
            res = urllib2.urlopen(apiUrl)
            result = res.read()
            time.sleep(1)
            count -= 1
        if result == '-3':
            return None
        return result

    def recognize(self, image_path, code_type):
        if not os.path.isfile(image_path):
            return False
        result = self.upload(image_path, code_type, 1)
        if result:
            token = result.split('|')
            if len(token) > 1:
                return token[1]
            return self.get_result(result);
        return None


def main():
    api = uuApi("soft_id", "soft_key", "user_name", "user_password")
    if api.enable():
    	print api.recognize("captcha.jpg", 1004)

if __name__ == '__main__':
    main()