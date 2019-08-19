# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import send_email
import send_dooray
import http.cookiejar, urllib.request
import re

def write_file(title) :
	with open('iros_title.txt',mode='a+',encoding='utf8') as title_file:
		title_file.write(title)
		title_file.close()

#공지사항 내용 중 기간관련 문자열 추출 식
def date_nomalization(item) :

	#1996.03.14 와 같은 내용 추출
	match = re.search(r"\d{2,4}\.\d{1,2}\.\d{1,2}",item)

	#연 월 일 관련 내용이 존재하지 않을때 다음 조건문에 들어간다
	if match is None :
		#03.14와 같이 월 일로 표현된 내용 추출
		match = re.search(r"\d{1,2}\.\d{1,2}",item)	
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%m.%d')
	else:
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%Y.%m.%d')

	#일시 datetime 형식으로 문자열 변환한 이후 반환
	return stop_date

#==========================================================================================================================================#
#메일에 들어갈 내용
mail_body = {}
abort_date = None
abort_thing = None
abort_why = None

#오늘날짜
today = datetime.today()
tomorrow =today + timedelta(days = 1)
year = str(today.year)
month = str(today.month)
#==========================================================================================================================================#


def go():

	# make session
	cj =   http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

	# access to notification page and get html
	html = opener.open("http://www.iros.go.kr/pos1/pfrontservlet?cmd=PCMS6GetBoardC&menuid=001004003001&boardTypeID=2&category=").read()

	# parse html
	soup = BeautifulSoup(html, "html.parser")

	# find noti title / date / content
	noti_list = []
	noti_table = soup.find(name="table")
	for tr in noti_table.find_all(name="tr"):
		if tr.td == None: continue	# skip when td is None

		# get title / date
		title = str(tr.td.get_text().strip())
		date = str(tr.td.next_sibling.next_sibling.string)
		print(year)
		print(date)
		# test compare date with this year
		if year in date :
			# access noti detail page for get content
			html = opener.open("http://www.iros.go.kr" + tr.a["href"]).read()	

			# parse html
			sub_soup = BeautifulSoup(html, "html.parser")
			for br in sub_soup.find_all("br"):
				br.replace_with("\n")	

			# get content
			content = sub_soup.find(class_="view_con")
			content_str = content.get_text()
			content_str = str(content_str.strip())

			# append noti_list
			noti = { 
				"title":title,
				"date":date,
				"content":content_str
				}
			noti_list.append(noti)

	noti_list.sort(key=lambda x: x["date"], reverse=True)
	print("pass")
	if len(noti_list) == 0:
		# send_email.send("인터넷 등기소", mail_body)
		return 
	else:
		print("pass2")
		new = True

		for noti in noti_list:
			abort_date = None
			abort_why = None
			abort_thing = None
			with open('iros_title.txt',mode='a+',encoding='utf8') as title_file:
				title_file.seek(0)
				while True:
					templine = title_file.readline()
					if not templine: break
					if templine == title:
						new = False
						break
				print(new)
				if new is False:
					for item in noti["content"].split("○"):
						#print "item : ", item
						#abort_date
						if abort_date is None and "중단일시" in item and "중단대상" in item:
							write_file(title)
							#정규식을 이용한 중단 일시 추출
							date_nomalization(item)
							#datetime 형식 문자열 변환
							stop_date = datetime.strptime(stop_date,'%Y.%m.%d')
							#중단 일시와 오늘 날짜, 내일날짜 비교 => 오늘 또는 내일일 경우 메일에 저장
							if (stop_date.day == tomorrow.day and stop_date.month == tomorrow.month) or (stop_date.day == today.day and stop_date.month == today.month) :
								abort_date = item[:item.index('중단대상')] 
						
						if "중단일시"  in item and abort_date is None :
							write_file(title)
							mail_body[noti["title"]] = abort_date
							#정규식을 이용한 중단 일시 추출
							date_nomalization(item)
							#datetime 형식 문자열 변환
							stop_date = datetime.strptime(stop_date,'%Y.%m.%d')
							#중단 일시와 오늘 날짜, 내일날짜 비교 => 오늘 또는 내일일 경우 메일에 저장
							if (stop_date.day == tomorrow.day and stop_date.month == tomorrow.month) or (stop_date.day == today.day and stop_date.month == today.month) :
								abort_date = item
						
						if "중단 일시" in item:
							write_file(title)
							mail_body[noti["title"]] = abort_date
							#정규식을 이용한 중단 일시 추출
							date_nomalization(item)
							#datetime 형식 문자열 변환
							stop_date = datetime.strptime(stop_date,'%Y.%m.%d')
							#중단 일시와 오늘 날짜, 내일날짜 비교 => 오늘 또는 내일일 경우 메일에 저장
							if (stop_date.day == tomorrow.day and stop_date.month == tomorrow.month) or (stop_date.day == today.day and stop_date.month == today.month) :
								abort_date = item[item.find('중단 일시'):item.index('※')]
							#abort_why
						if "중단사유" in item or "작업사유" in item:
							abort_why = item[item.find('작업사유'):]			
							#abort_thing
						if "중단대상" in item:
							abort_thing = item[item.find('중단대상'):item.find('※')]

						if abort_date :
							send_dooray.send("인터넷 등기소", noti["title"], noti["content"])
							send_email.send("인터넷 등기소", mail_body)	

