# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import datetime
import send_email
import send_dooray

#===================================================#
#메일에 들어갈 내용
mail_body = {}

#오늘날짜
today = datetime.datetime.now()
#===================================================#

def go():
	db_list = []

	req = requests.get('http://www.kcredit.or.kr/content/noticeList.do')
	html = req.text
	soup = BeautifulSoup(html, 'html.parser')

	titles = soup.find_all('a', {"class":"link searchList"})

	date = soup.find_all('td')
	
	count = 0
	#날짜먼저 확인(오늘날짜인지?), 6i+3
	for i in range(len(date)):
		index = 6*i+3

		if index < len(date) and date[index].get_text() == today.strftime("%Y.%m.%d"):
			count += 1

	#connect detail page
	for i in range(count):
		
		ahref = "http://www.kcredit.or.kr"+titles[i]['href']
		sub_req = requests.get(ahref)
		sub_html = sub_req.text
		soup = BeautifulSoup(sub_html, 'html.parser')

		title = soup.find('h4').get_text()
		content = soup.find("div", {"class":"view_main"}).get_text()
		utf_title = title.encode('utf-8')
		utf_content = content.encode('utf-8')
		
		mail_body[utf_title] = content.encode('utf-8')
		send_dooray.send("신용정보원(KCB)", title.decode(), utf_content.decode())

	#send_email.send("신용정보원(KCB)", mail_body)