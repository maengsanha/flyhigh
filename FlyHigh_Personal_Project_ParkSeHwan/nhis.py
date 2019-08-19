# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib
import json
import time
from datetime import datetime,timedelta
import send_email
import send_dooray
import re

def date_nomalization(item) :
	#1996-03-14 와 같은 내용 추출(연 월 일)
	match = re.search(r"\d{4}\-\d{1,2}\-\d{1,2}",item)
	#연 월 일 관련 내용이 존재하지 않을때 다음 조건문에 들어간다
	if match is None :
		match = re.search(r"\d{1,2}\-\d{1,2}",item)
		if match is None :
			#03.14와 같이 월 일로 표현된 내용 추출
			return datetime.strptime('9999-12-31','%Y-%m-%d')
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%m-%d')
	else:
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%Y-%m-%d')
	#일시 datetime 형식으로 문자열 변환한 이후 반환
	return stop_date

#===================================================#
#메일에 들어갈 내용
mail_body = {}
abort_date = None
abort_thing = None
abort_why = None

#오늘날짜
today = datetime.today()
tomorrow =today + timedelta(days = 1)
#===================================================#


def once_go():
	noti_data = {}

	req = urllib.request.urlopen("https://si4n.nhis.or.kr/jpza/JpZaa00101.do")

	html = req.read()
	soup = BeautifulSoup(html, "html.parser")

	noti_data["banner"] = []
	
	# find all banner from front page
	banner_list = soup.find_all("div", attrs={"class", "banner"})

	for banner in banner_list:
	    # skip when invisible div
	    if "display:none;" in banner.attrs["style"]:
	        continue

	    # make dict
	    banner_dict = {}
	    li_list = banner.find_all("li")
	    if len(li_list) >= 3:
	        banner_dict["term"] = li_list[0].contents[1].strip()
	        banner_dict["reason"] = li_list[1].contents[1].strip()
	        banner_dict["target"] = li_list[2].contents[1].strip()

	        abort_date = banner_dict["term"]
	        abort_why = banner_dict["reason"]
	        abort_thing = banner_dict["target"]
	        title = "점검 일정"
	        content = "공단은 국민들에게 더 나은 인터넷 서비스를 제공하고자 다음과 같이 시스템 점검을 실시함을 알려드립니다."
        	send_dooray.send("건강보험공단(+사회보험통합징수포털)", title, abort_date)

def go():

	#페이지 접속
	req = requests.get("https://www.nhis.or.kr/bbs7/boards/B0040/rss")
	html = req.text
	soup = BeautifulSoup(html, 'html.parser')
	
	#공지 테이블
	table = soup.find('channel')
	#제목, 게시일 찾기
	titles = table.find_all('title')
	
	titles_link = table.find_all('guid')
	
	for i in range(1,len(titles_link),1):
		ahref = titles_link[i-1].text.strip()
		ahref = ahref[:ahref.find('bbs7')+5]+'boards/'+ahref[ahref.find('bbs7')+5:]
		
		#각 공지사항 확인
		sub_req = requests.get(ahref)
		sub_html = sub_req.text
		sub_soup = BeautifulSoup(sub_html,'html.parser')
		content = sub_soup.find('div',{'class':'view_con'})
		
		#공지 제목과 공지일 빼오는 부분
		noti_content = sub_soup.find('tbody')
		noti_title = titles[i-1].text.strip()
		noti_date = date_nomalization(noti_content.text.strip())
		
		#오늘 날짜 추출
		convert_to_date = today.strftime("%Y-%m-%d")	
		is_write = True	

		#공지 글이 오늘 일자와 같은가
		if convert_to_date == noti_date:
			# 이미 읽은 공지인가 여부 확인
			with open('nhis_title.txt',mode='a+',encoding='utf8') as title_file:
				title_file.seek(0)
				templine = title_file.readlines()
				# 파일에 내용이 없으면 안보낸 공지임으로 is_write = True
				if not templine: 
					is_write = True
				else:	
	 				#기존에 읽었으면 False
					if noti_title in templine:
						is_write = False
			
			print(is_write)
			# 안읽은 공지일 경우 전송 
			if is_write : 
				title_file = open('nhis_title.txt', mode='a+', encoding='utf8')
				title_file.write(noti_title + '\n')
				send_dooray.send("건강보험공단(+사회보험통합징수포털)", noti_title,content.text.strip())
				send_email.send('nhis',noti_title,content.text.strip())

		
		
		