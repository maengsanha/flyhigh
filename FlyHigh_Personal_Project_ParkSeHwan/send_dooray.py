# -*- coding:utf-8 -*-
import urllib.request as url_req
import json

def send_dooray_noti(url, data):
	req = url_req.Request(url, json.dumps(data).encode('utf-8'), {'Content-Type': 'application/json'})
	return url_req.urlopen(req)

def send(sitetype, title, content):

	data = {
		"botName" : "DocBot",
		"botIconImage" : "https://translate.nhnent.com/icon/botimage.jpg",
		"text" :  sitetype + " 공지 확인 결과",
		"attachments": [
			{
				"title": title, 
				"text": content,
				"color": "#FFD700"
			}
		]
	}
	send_dooray_noti("https://hook.dooray.com/services/2271045959672406714/2516625870683380315/RdkbXY2IQPOrMkXkzMJRoQ", data)

def test_send(sitetype, title, content):

	data = {
		"botName" : "DocBot",
		"botIconImage" : "https://translate.nhnent.com/icon/botimage.jpg",
		"text" :  sitetype + " 공지 확인 결과",
		"attachments": [
			{
				"title":  title, 
				"text": content,
				"color": "#FFD700"
			}
		]
	}
	send_dooray_noti("https://hook.dooray.com/services/2271045959672406714/2418073129534065736/2nkpAeNiQDaGVzhuua661Q", data)
