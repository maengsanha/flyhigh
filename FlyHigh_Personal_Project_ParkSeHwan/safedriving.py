# -*- coding:utf-8 -*-
from selenium import webdriver
from email.mime.image import MIMEImage
import datetime
import os
import send_email
import send_dooray
import datetime


def go():

	#===================================================#
	#메일에 들어갈 내용
	mail_body = {}
	abort_date = "N"
	abort_thing = "N"
	abort_why = "N"

	#오늘날짜
	today = datetime.datetime.now()
	#===================================================#

	driver = webdriver.Chrome()
	driver.get("https://www.safedriving.or.kr/main.do")

	#화면 최대화
	driver.maximize_window()

	#스크린샷
	filename = os.getcwd() + "/todayscreen" + ".png"
	shot = driver.get_screenshot_as_file(filename)

	#MIMEImage로 변환 
	fp = open(filename, 'rb')
	context = fp.read()
	img = MIMEImage(context)
	context = str(context)
	fp.close()

	is_write = True
	#이전 시간에 보냈는지 확인
	with open('safedriving.txt', mode='a+', encoding='utf8') as title_file:
		title_file.seek(0)
		templine = title_file.read()
		#파일에 내용이 없으면 False
		if not templine: 
			is_write = False
		#기존에 읽었으면 True
		if( context == templine):
			is_write = True
				
	if is_write is False : 
		with open('safedriving.txt', mode='w', encoding='utf8') as title_file:
			title_file.write(context)
		send_email.send("도로교통공단 안전운전 통합민원",dict=[], attach_img=img)

	driver.quit()