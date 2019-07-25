# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import send_email
import send_dooray
import re

#공지사항 내용 중 기간관련 문자열 추출 식
def date_nomalization(item) :

	#1996.03.14 와 같은 내용 추출
	match = re.search(r"\d{4}\.\d{1,2}\.\d{1,2}",item)

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

def go():
	#===================================================#
	#메일에 들어갈 내용
	mail_body = {}

	#오늘날짜 와 내일날짜
	today_date = datetime.today()
	tomorrow =today_date + timedelta(days = 1)

	#===================================================#
	
	#사이트 접속
	req = requests.get('http://www.minwon.go.kr/main?a=AA140NoticeListApp&cp=1')
	html = req.text

	#데이터 수집'
	soup = BeautifulSoup(html, 'html.parser')

	#find noti table
	table = soup.find('tbody')

	#공지 세부 페이지 접속을 위해 공지사항 제목을 모두 찾아서 한번씩 접속해보기
	titles = table.find_all('td', {'class':'tl'}) 

	for i in range(len(titles)):
		#메일에 들어갈 내용정보 초기화
		abort_date = None
		abort_thing = None
		abort_why = None

		#공지 세부 페이지 접속
		current_title = titles[i]
		title_link = current_title.find('a')
		ahref = "http://www.minwon.go.kr"+title_link['href']

		sub_req = requests.get(ahref)
		sub_html = sub_req.text

		#데이터 수집
		soup = BeautifulSoup(sub_html, 'html.parser')

		#세부 페이지에서 공지 제목과 날짜 수집
		title_date = soup.find_all('dd', {'class':'w02'})

		#제목
		title = title_date[0].get_text()
		
		#날짜
		date_to_string = title_date[1].get_text()
		formatting = date_to_string.replace(" ", "0")

		#날짜 포맷 변경
		string_to_date = datetime.strptime(formatting, "%Y.%m.%d.")
	
		#오늘 공지가 올라왔나?
		is_today_new = True
		#이미 메일로 전송한 내용인가
		is_write = False

		#올해, 오늘 날짜의 새로운 공지가 있니?
		if string_to_date.year == today_date.year:
			if string_to_date.strftime("%Y%m%d") == today_date.strftime("%Y%m%d"):
				is_today_new = True
			else:
				is_today_new = False	
		else:
			continue
		#이전 시간에 보냈는지 확인
		with open('mw24_title.txt', mode='a+', encoding='utf8') as title_file:
			title_file.seek(0)
			#이전에 메일로 전송한 내용이니?
			while True:
				templine = title_file.readlines()
				#파일에 내용이 없으면 break
				if not templine: break
	 			#기존에 읽었으면 False
				if(title.strip() in templine.strip()):
					is_write = True
					break	
		print("is_write : ", is_write)
		#이미 전송했던 내용 통과
		if is_write :
			continue

		#공지사항에서 오늘 날짜에 공지된 공지사항 중 오늘 내일간 일정이 시작되는 공지를 전송 
		if is_today_new:
		
			#해당 공지 내용을 수집
			content = soup.find('dd',{'class':'w_all pl5 pt5'})
			
			#공지 세부 내용
			string_content = content.text
			utf_content = string_content	

			#내용 쪼개기 : 중단 일시, 작업사유, 중단 대상 업무
			#일시관련 내용이 나오면 다음과 같이 처리
			#일시 : 오늘 or 내일일때 -> 그 날 바로 내용전송 
			#일시 : 그 이외의 일자일 때 -> 해당 일자 파일에 저장	
			for item in utf_content.split("\n"):				
				#abort_date
				if "중단일시" in item:

					#정규식을 이용한 중단 일시 추출
					date_nomalization(item)
					#datetime 형식 문자열 변환
					stop_date = datetime.strptime(stop_date,'%Y.%m.%d')
					#중단 일시와 오늘 날짜, 내일날짜 비교 => 오늘 또는 내일일 경우 메일에 저장
					if  (stop_date.day == tomorrow.day and stop_date.month == tomorrow.month) or (stop_date.day == today_date.day and stop_date.month == today_date.month) :
						abort_date = item[item.find('중단일시'):item.find('중단일시')+68]
					
				if "작업일시" in item:
					#정규식을 이용한 작업 일시 추출
					date_nomalization(item)
					#datetime 형식 문자열 변환
					stop_date = datetime.strptime(stop_date,'%Y.%m.%d')

					#작업 일시와 오늘 날짜 비교
					if  (stop_date.day == tomorrow.day and stop_date.month == tomorrow.month) or (stop_date.day == today_date.day and stop_date.month == today_date.month) :
						abort_date = item


				#abort_why
				if "작업사유" in item:
					abort_why = item[item.find('작업사유'):item.find('○')]
				if "중단사유" in item:
					abort_why = item[item.find('중단사유'):]
				if "작업내용" in item:
					abort_why = item		
					#abort_thing
				if "중단업무" in item:
					abort_thing = item[item.find('중단업무'):]
				if "중단서비스" in item:
					abort_thing = item

		#공지사항에서 이전 날짜에 공지된 공지사항 중 내일 일정이 시작되는 공지를 전송 
		else:	

			#해당 공지 내용을 수집
			content = soup.find('dd',{'class':'w_all pl5 pt5'})
			#공지 세부 내용
			string_content = content.text
			utf_content = string_content	

			#내용 쪼개기 : 중단 일시, 작업사유, 중단 대상 업무
			#일시관련 내용이 나오면 다음과 같이 처리
			#일시 : 오늘 or 내일일때 -> 그 날 바로 내용전송 
			#일시 : 그 이외의 일자일 때 -> 해당 일자 파일에 저장	
			for item in utf_content.split("\n"):				
				#abort_date
				if "중단일시" in item:
					#정규식을 이용한 중단 일시 추출
					date_nomalization(item)
					
					#중단 일시와 오늘 날짜 비교
					if  stop_date.day == tomorrow.day and stop_date.month == tomorrow.month:
						abort_date = item[item.find('중단일시'):item.find('중단일시')+68]
							
				if "작업일시" in item:
					#정규식을 이용한 작업 일시 추출
					date_nomalization(item)
						#작업 일시와 오늘 날짜 비교
					if  stop_date.day == tomorrow.day and stop_date.month == tomorrow.month:
						abort_date = item
			
				#abort_why
				if "작업사유" in item:
					abort_why = item[item.find('작업사유'):item.find('○')]
				if "중단사유" in item:
					abort_why = item[item.find('중단사유'):]
				if "작업내용" in item:
					abort_why = item		
					#abort_thing
				if "중단업무" in item:
					abort_thing = item[item.find('중단업무'):]
				if "중단서비스" in item:
					abort_thing = item
			

		#오늘 보낼 내용지 존재한다면 메일 전송
		if abort_date:
			#오늘 보낼 내용이 존재한다면 해당 공지사항 제목 파일에 적어놓기
			title_file = open('mw24_title.txt', mode='a+', encoding='utf8')
			title_file.write(title+'\n')
			title_file.close()
			mail_body[title] = abort_date
			#메일 및 두레이 전송
			send_email.send("민원24", mail_body)
			send_dooray.send("민원24", title, utf_content)

#to do 팝업이 새로 올라올때만 접속해서 확인하자.
def go_popup():

	is_today_popup_new = True
	#===================================================#
	#메일에 들어갈 내용
	mail_body = {}
	abort_date = "N"
	abort_thing = "N"
	abort_why = "N"

	#===================================================#
	
	#민원 팝업 열기
	req = requests.get('http://www.minwon.go.kr/popup/routine_notice.jsp')
	html = req.text
	#html 제목 파싱
	soup = BeautifulSoup(html, 'html.parser')
	title = soup.find('title').text.strip()
	print(title)

	#공지사항 날짜 추출	
	why = soup.find('div', {'id':'m2'})
	abort_why = why.text.strip()
	date_and_thing = soup.find_all('div', {'id':'date_imsi'})
	abort_date = date_and_thing[0].text.strip()

	#오늘 내일 날짜 확인 및 문자열 변환
	today_date = datetime.today()
	today = today_date.strftime("%Y.%m.%d")
	tomorrow =today_date + timedelta(days = 1)

	#문자열 정리
	abort_real_date = abort_date[abort_date.find("○"):abort_date.find("~")+1]
	abort_real_date += abort_date[abort_date.find("~")+15:]
	abort_thing = date_and_thing[1].text.strip()

	#정규식을 이용한 중단 일시 추출
	match = re.search(r"\d{4}\.\d{1,2}\.\d{1,2}",abort_real_date)
	stop_date = abort_real_date[ match.start():match.end()]
	stop_date = datetime.strptime(stop_date,'%Y.%m.%d')

	#중단 일자가 오늘,내일일 경우  
	if today == stop_date or stop_date == tomorrow.strftime('%Y.%m.%d'):
		print("date is : ",stop_date.day)
		#기존에 읽은 공지사항인지를 확인
		with open('mw24_pop_title.txt', mode='a+', encoding='utf8') as popup_title_file:
			popup_title_file.seek(0)
			while True:
				templine = popup_title_file.readline()
				if not templine: break
				#기존에 읽었으면 False
				if(templine in abort_real_date):
					is_today_popup_new = False
					break

		#새로운 공지사항이 업데이트 되었을 때  
		if(is_today_popup_new):

			#두레이 전송 내용 
			content = abort_why+ '\n' + abort_real_date + '\n' + abort_thing
			mail_body[title] = abort_real_date
			#파일에 오늘 올라온 공지 내용 쓰기 (다음번에 이 내용과 비교하여 업데이트 유무를 비교 )
			with open('mw24_pop_title.txt', mode='w', encoding='utf8') as popup_title_file:
				popup_title_file.write(abort_real_date)
			#두레이 및 이메일 전송
			send_email.send("민원24-팝업", mail_body)
			send_dooray.send('mw24-popup', title, content)
			popup_title_file.close()		
		
#if __name__ == "__main__":
#	go()