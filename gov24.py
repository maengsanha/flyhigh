# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import send_email
import send_dooray
import re

#공지사항 내용 중 기간관련 문자열 추출 식
def date_nomalization(item) :
	#1996.03.14 와 같은 내용 추출(연 월 일)
	match = re.search(r"\d{4}\.\d{1,2}\.\d{1,2}",item)
	
	#연 월 일 관련 내용이 존재하지 않을때 다음 조건문에 들어간다
	if match is None :
		match = re.search(r"\d{1,2}\.\d{1,2}",item)
		if match is None :
			#03.14와 같이 월 일로 표현된 내용 추출
			return datetime.strptime('9999.12.31','%Y.%m.%d')
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%m.%d')
	else:
		stop_date = item[match.start():match.end()]
		stop_date = datetime.strptime(stop_date,'%Y.%m.%d')
	#일시 datetime 형식으로 문자열 변환한 이후 반환
	return stop_date

def go():
	print("=" * 25 + "gov24" + "=" * 25)

	#===================================================#
	#메일에 들어갈 내용
	mail_body = {}

	#오늘날짜
	today = datetime.today()
	tomorrow =today + timedelta(days = 1)
	#===================================================#
	
	#페이지 접속
	req = requests.get('https://www.gov.kr/portal/ntcItm')
	html = req.text
	soup = BeautifulSoup(html, 'html.parser')

	#공지 테이블
	table = soup.find('tbody')

	#제목, 게시일 찾기
	titles_dates = table.find_all('td', {'class':'m-show'})


	#인덱스 홀수는 날짜, 짝수(0포함)는 제목(링크)
	for i in range(1, len(titles_dates), 2):
		#메일에 들어갈 내용정보 초기화
		abort_date = None
		abort_thing = None
		abort_why = None
		
		#HTML 태그 제거
		string_dates = titles_dates[i].text.strip()

		#날짜 포맷 변경
		convert_to_date = datetime.strptime(string_dates, "%Y.%m.%d") 
		
		#제목 선택
		current_title = titles_dates[(i-1)]
		title_link = current_title.find('a')
		title = current_title.text
		
		#상세 페이지 이동
		ahref = "https://www.gov.kr"+title_link['href']
		sub_req = requests.get(ahref)
		html = sub_req.text
		sub_soup = BeautifulSoup(html, 'html.parser')
		content = sub_soup.find('div',{'class':'view-contents'})

		#공지 세부 내용
		string_content = content.text
		utf_content = string_content
		#split return list
		#ex) "this is me" > split(" ") > ["this", "is", "me"]

		#이미 이메일에 전송한 공지인가 여부
		is_write = True
		#오늘 올라온 공지인가 여부
		is_today_new = True
		#오늘 날짜 문자열 추출
		today_date=today.strftime("%Y.%m.%d")

		#오늘날짜의 새로운 공지가 있니?
		if convert_to_date.year == today.year :
			if convert_to_date == today_date:
				is_today_new = True
			else:
				is_today_new = False
		else:
			continue

		#이미 보낸 내용인지를 확인하는 부분
		with open('gov24_title.txt',mode='a+',encoding='utf8') as title_file:
			title_file.seek(0)
			templine = title_file.readlines()
			#파일에 내용이 없으면 break(이미 보낸 내용 X)
			if not templine: 
				is_today_new = True	
			else:	
	 			#기존에 읽었으면 False
				if title.strip() in str(templine):
					is_write = False
		
		print("is_write : ",is_write)
		#이미 읽은 공지는 건너뛰기
		if is_write is False:
			continue	

		#오늘 올라온 공지사항인가
		if is_today_new :
			for item in utf_content.split("○"):		
				#abort_why
				if "작업사유" in item:
					abort_why = item[item.find('작업사유'):item.find('※')]+'\n'
				elif "중단사유" in item:
					abort_why = item+'\n'
				elif "작업내용" in item:
					abort_why = item[item.find('작업내용'):item.find('작업내용')+62]+'\n'
				elif "중단 사유" in item:
					abort_why = item[item.find('중단 사유'):item.find('※')]+'\n'
				#abort_thing
				if "중단업무" in item:
					abort_thing = item[item.find('중단업무'):item.find('※')]+'\n'
				if "중단 업무" in item:
					abort_thing = item+'\n'
				if "중단서비스" in item:
					abort_thing = item[item.find('중단서비스'):]+'\n'
				if "대상" in item:
					abort_thing = item +'\n'

				#abort_date
				#정규식 데이터 추출 -> 오늘,내일과 날짜 비교 -> 일치할시 메일 내용에 팝업내용 저장
				if "중단일시" in item:
					stop_day =date_nomalization(item)
					if  (stop_day.day == tomorrow.day and stop_day.month == tomorrow.month) or (stop_day.day == today.day and stop_day.month == today.month) :
						abort_date = item[item.find("중단일시"):item.find("중단일시")+43]+'\n'
				if "작업일시" in item: 
					stop_day = date_nomalization(item)
					if  (stop_day.day == tomorrow.day and stop_day.month == tomorrow.month) or (stop_day.day == today.day and stop_day.month == today.month) :
						abort_date = item[item.find('작업일시'):item.find('작업일시')+43]+'\n'
				if "중단 시간" in item and abort_date == "N":
					stop_day = date_nomalization(item)
					if  (stop_day.day == tomorrow.day and stop_day.month == tomorrow.month) or (stop_day.day == today.day and stop_day.month == today.month) :
						abort_date = item[item.find("중단 시간"):item.find("중단 시간")+43]+'\n'
				if "기간" in item:
					stop_day = date_nomalization(item)
					if  (stop_day.day == tomorrow.day and stop_day.month == tomorrow.month) or (stop_day.day == today.day and stop_day.month == today.month) :
						abort_date = item[item.find("기간"):item.find("기간")+37]+'\n'
			
		
		else :
			for item in utf_content.split("○"):		
				#abort_why
				if "작업사유" in item:
					abort_why = item[item.find('작업사유'):item.find('※')]+'\n'
				elif "중단사유" in item:
					abort_why = item+'\n'
				elif "작업내용" in item:
					abort_why = item[item.find('작업내용'):item.find('작업내용')+62]+'\n'
				elif "중단 사유" in item:
					abort_why = item[item.find('중단 사유'):item.find('※')]+'\n'
				#abort_thing
				if "중단업무" in item:
					abort_thing = item[item.find('중단업무'):item.find('※')]+'\n'
				if "중단 업무" in item:
					abort_thing = item+'\n'
				if "중단서비스" in item:
					abort_thing = item[item.find('중단서비스'):]+'\n'
				if "대상" in item:
					abort_thing = item +'\n'

				#abort_date
				#정규식 데이터 추출 -> 오늘,내일과 날짜 비교 -> 일치할시 메일 내용에 팝업내용 저장
				if "중단일시" in item:
					stop_day = date_nomalization(item)
					if  stop_day.day == tomorrow.day and stop_day.month == tomorrow.month:
						abort_date = item[item.find("중단일시"):item.find("중단일시")+43]+'\n'

				if "작업일시" in item: 
					stop_day = date_nomalization(item)
					if  stop_day.day == tomorrow.day and stop_day.month == tomorrow.month:
						abort_date = item[item.find('작업일시'):item.find('작업일시')+43]+'\n'
				if "중단 시간" in item and abort_date == "N":
					stop_day = date_nomalization(item)
					if  stop_day.day == tomorrow.day and stop_day.month == tomorrow.month:
						abort_date = item[item.find("중단 시간"):item.find("중단 시간")+43]+'\n'
				if "기간" in item:
					stop_day = date_nomalization(item)
					if  stop_day.day == tomorrow.day and stop_day.month == tomorrow.month:
						abort_date = item[item.find("기간"):item.find("기간")+37]+'\n'
			
		if abort_date :
			#메일에 보낼 내용이 존재할 때
			#파일에 내용 입력
			title_file = open('gov24_title.txt', mode='a+', encoding='utf8')
			title_file.write(title.strip() + '\n')
			title_file.close()
			#메일 및 두레이 전송
			send_dooray.send("정부24", title, utf_content)
			utf_title = title
			mail_body[utf_title] = abort_date
			send_email.send("정부24", mail_body)
				