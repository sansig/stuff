# coding: utf-8
import re
import linecache
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
#import mysql.connector 	#For Windows mysql access
import MySQLdb 				#For linux mysql access
logging.basicConfig(level=logging.INFO)
urls = {}
db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
cursor = db.cursor(MySQLdb.cursors.DictCursor)
cursor.execute('SELECT * FROM `tbl_gyms` WHERE `tbl_gyms`.`fresh` = 0')
for row in cursor.fetchall():
	urls[row['gym_name']] = 'https://gymhuntr.com/#' + str(row['lat']) + ',' + str(row['lon'])
db.close()
	
def parse_map():
	driver.find_element_by_xpath('//div[contains(@class, "leaflet-marker-icon")]').click()
	driver.find_element_by_id('scan').click()
	time.sleep(90)
	gyms = driver.find_elements_by_xpath('//div[contains(@class, "gym")]')
	logging.info(len(gyms))
	if(len(gyms) > 0):
		logging.info('Parsing gyms')
		parse_gyms(gyms)

def parse_gyms(gyms):
	i =0
	for g in gyms:
		try:
			g.click()
		except:
			logging.info('Off-screen')
		else:
			i +=1
			f = check_gym()
			time.sleep(1)

def check_gym():
	status = driver.find_element_by_xpath('//div[@class="last_scanned"]').text
	if status == "Last scanned minutes ago":
		fresh = 1
	else:
		fresh = 0
	a = driver.find_element_by_xpath('//div[@class="popupfoot"]/a').get_attribute('href')
	m = re.findall('([\d\.\-]+),([\d\.\-]+)', a)
	lat = m[0][0]
	lon = m[0][1]
	sql = "UPDATE tbl_gyms SET fresh = %s WHERE lat = %s AND lon = %s"
	sql_data = (fresh, lat,lon)
	db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute(sql, sql_data)


for u in urls:
	driver = webdriver.PhantomJS(executable_path='/home/user/path/to/phantomjs') #CHANGE THIS
	driver.set_window_size(2000,2000)
	try:
		logging.info(u)
		driver.get(urls[u])
		if driver.current_url != urls[u]:
			logging.error('Url not loaded')
		logging.info('Searching for data...')
		parse_map()
	except:
		logging.error('Error with the phantom module')
	finally:
		driver.close()
		driver.quit()
logging.info('Completed')