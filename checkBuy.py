import urllib2,time,random,socket,smtplib
from email.mime.text import MIMEText

MAXTIME_WAIT = 60
CONFIG_PATH = '/root/checkBuy/checkBuy.config'
MAIL_PATH = '/root/checkBuy/notice.mail'
mail_info = []
webCheckList = []

#"User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
#"Accept-Encoding": "gzip, deflate",
#"Cookie": "_ga=GA1.3.385064905.1452777752; __auc=ca91bcf3152404d44885c402e2c; ckFORUM_bsn=0; ckBahaAd=8-----4---------; __asc=3f0f58e5153218cdfd3bf504fb4; _gat=1; ckBUY_item18UP=18UP"
###response.info()['Content-Encoding']
request_headers_noCookie = {
"Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Connection": "keep-alive"
}

request_headers_Cookie = {
"Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Connection": "keep-alive",
"Cookie": ""
}

def writeFile(filepath = None,buf = None) :
	f = open(filepath,'w')
	f.write(buf)
	f.close()

def sendMail(mailTitle = None,mailstr = None) :
	global mail_info

	socket.setdefaulttimeout(5)
	if not mail_info :
		print 'No setting linemail.config'
		return
	try :
		mg = MIMEText('%s' % mailstr)
		mg['Subject'] = '[checkBuy] %s just buy!' % mailTitle
		mg['From'] = mail_info[1]
		mg['To'] = mail_info[3]
		s = smtplib.SMTP(mail_info[0],timeout=1)
		s.login(mail_info[1],mail_info[2])
		s.sendmail(mg['From'],mg['To'].split(','),mg.as_string())
		s.quit()
		print "Send notice to %s" % mail_info[3]
	except Exception as e :
		print e
	return
		
def mailinfo() :
	mMail = []
	try :
		f = open(MAIL_PATH,"r")
	except Exception as e:
		print e
		return None
	strbuf = f.read()
	mMail = strbuf.split("\n")
	print mMail
	return mMail

def getConfig() :
	fileLine = []
	webSet = []
	f = open(CONFIG_PATH,'r')
	buf = f.read()
	fileLine = buf.split('\n')
	
	for line in fileLine :
		if line == '' or  line[0] == '\n' or line[0] == ' ' or line[0] == '\t' or line[0] == '#':
			continue
		if line[0] == '\xEF' and line[3] == '#' :
			continue
		webSet = line.split('\t')
		webCheckList.append(webSet)
	print len(webCheckList)
	f.close()
	return
	
def sleepTime() :
	sec = random.randint(3, MAXTIME_WAIT)
	print 'wait %d sec' % sec
	return sec
	
def checkURL() :
	request_headers = {}
	#for mIndex,tempbuf in enumerate(temp_list) :
	for mIndex,checkWeb in enumerate(webCheckList) :
		if len(checkWeb) > 4:
			print 'Alread send notify!'
			#continue
		webName = checkWeb[0]
		targetURL = checkWeb[1]
		checkString = checkWeb[2]

		if len(checkWeb) > 3 and checkWeb[3] != '' :
			request_headers = request_headers_Cookie
			request_headers["Cookie"] = checkWeb[3]
		else :
			request_headers = request_headers_noCookie
			#webCheckList[mIndex].append('')

		print targetURL
		print checkString
		print request_headers
		myRrequest = urllib2.Request(targetURL, headers=request_headers)
		try :
			response = urllib2.urlopen(myRrequest,timeout=3)
		except Exception as e :
			print e
			continue

		WebContent = response.read()
		
		ret = WebContent.find(checkString)

		print '==================='
		if ret == -1 :
			print '%s Can\'t buy' % webName
			filename = 'nobuy_%d.html' % mIndex
			writeFile(filename,WebContent)
		else :
			print '%s Buy it !' % webName
			sendMail(webName,response.geturl())
			checkWeb.append('')
			writeFile('/root/checkBuy/getBuy.html',WebContent)
		if mIndex +1 == len(webCheckList) :
			break
		print '...';
		time.sleep(5)
	return

def start() :
	global mail_info
	getConfig()
	mail_info = mailinfo()
	
	while(1) :
		checkURL()
		time.sleep(sleepTime())

	#join Cache to header
	#not handle gzip encode
	


	
		#sendMail('','')
	
	
	#<a href="javascript:preorder(19741,'wantorder')">
	#<img src="http://i2.bahamut.com.tw/newgshop/notify_buy.gif"></a>
	
	#<a href="javascript:BUY_notify('', '')">
	#<img src="http://i2.bahamut.com.tw/newgshop/order_new.gif"></a>

if __name__ == '__main__' :
	start()
