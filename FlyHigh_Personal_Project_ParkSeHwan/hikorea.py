# -*- coding:utf-8 -*-
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import send_email
import send_dooray


def go():
	#===================================================#
	#메일에 들어갈 내용
	mail_body = {}
	# abort_date = "N"
	# abort_thing = "N"
	# abort_why = "N"

	#오늘날짜
	today = datetime.datetime.now()
	#===================================================#
	
	driver = webdriver.Chrome()
	#하이코리아 접속
	driver.get("https://www.hikorea.go.kr/pt/main_kr.pt")
	
	#하이코리아 html 추출 
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	#공지사항 리스트 찾기
	td = soup.find('div', {'class':'bbs-list'})

	# 공지 글 찾기
	list = td.find_all('ul')

	# 공지 글 제목 찾기
	titles = td.find_all('span',{'class':'subject'})

	# 공지글 날짜 찾기
	dates = td.find_all('span',{'class':'date'})

	#공지글 링크 들어가기
	for i in range(1,len(dates),1):
		
		#공지글 날짜 추출
		noti_date = dates[i-1].text
		
		# 오늘 날짜 1996.03.14 와 같은 형식으로 변환
		convert_to_date = today.strftime("%Y.%m.%d")
		
		#이미 이메일에 전송한 공지인가 여부
		is_write = True
		
		# 해당 공지글이 오늘 올라왔는지 비교
		if convert_to_date == noti_date: 	

			#이미 보낸 내용인지를 확인하는 부분
			with open('hikorea_title.txt',mode='a+',encoding='utf8') as title_file:
				title_file.seek(0)
				templine = title_file.readlines()
				#파일에 내용이 없으면 break(이미 보낸 내용 X)
				if not templine: 
					is_write = True
				else:	
	 				#기존에 읽었으면 False
					if titles[i-1].text in templine:
						is_write = False

			if is_write :		
				with open('hikorea_title.txt',mode='a+',encoding='utf8') as title_file:
					title_file.write(titles[i-1].text)

				# 공지사항 링크 추출
				href = list[i-1].find('a')
				ahref = href['href']

				# 해당 공지글 접근
				sub_req = requests.get(ahref)
				html = sub_req.text
				sub_soup = BeautifulSoup(html, 'html.parser')
				# 해당 공지글 내용 추출
				content = sub_soup.find('td',{'class':'tdContents'})

				#두레이 및 이메일 전송
				send_dooray.send("하이코리아", titles[i-1].text, content.text)
				utf_title = titles[i-1].text
				mail_body[utf_title] = content.text
				send_email.send("하이코리아", mail_body)
				
	driver.quit()
	#0 <td class="tdData C">687</td>, 
	#1 <td class="tdData">\n<a href="/pt/NtcCotnDetailR_kr.pt?pageSpec=&amp;targetRow=&amp;lafjOrderBy=&amp;sRange=&amp;sKeyWord=&amp;newscttSeq=886&amp;bbsGbCd=BS10&amp;langCd=KR&amp;pageCode=list&amp;bbsSeq=1&amp;bbsNm=\uacf5\uc9c0\uc0ac\ud56d" onclick="fncDetailNtc('886');return false;" onkeypress="fncDetailNtc('886');return false;">\ucd9c\uc785\uad6d\ubbfc\uc6d0\ub300\ud589\uae30\uad00 \ubcc4\ub3c4\ucc3d\uad6c \uc6b4\uc601\uae30\uad00 \uc54c\ub9bc</a>\n</td>
	#2 <td class="tdData C">HiKorea</td>, 
	#3 <td class="tdData C">2019.05.14</td>

	