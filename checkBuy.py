import urllib2,time,random,socket,smtplib,chardet,zlib
from email.mime.text import MIMEText

MAXTIME_WAIT = 60
CONFIG_PATH = '/root/Program/checkBuy/checkBuy.config'
MAIL_PATH = '/root/Program/checkBuy/notice.mail'
GET_HTML = '/root/Program/checkBuy/getBuy.html'
mail_info = []
webCheckList = []

request_headers_noCookie = {
"Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36",
"Upgrade-Insecure-requests":"1",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Connection": "keep-alive"
}

request_headers_Cookie = {
"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"accept-language":"zh-TW,zh,en-US;q=0.8,en;q=0.7",
"cache-control":"max-age=0",
"cookie": "",
"if-modified-since":"Wed, 03 Oct 2018 02:30:15 GMT",
"upgrade-insecure-requests":"1",
"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
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

	for mIndex,checkWeb in enumerate(webCheckList) :
		if checkWeb[2] == '#':
			print '%s %s Alread send notify!' % (checkWeb[0],checkWeb[1])
			continue
		webName = checkWeb[0]
		targetURL = checkWeb[1]
		checkString = checkWeb[2]

		if len(checkWeb) > 3 and checkWeb[3] != '' :
			request_headers = request_headers_Cookie
			request_headers["Cookie"] = checkWeb[3]
		else :
			request_headers = request_headers_noCookie

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

  		# for check get html
		# gzipped = response.headers.get('Content-Encoding')
		# print 'gzipped ##'
		# print gzipped

		# if gzipped :
		# 	html = zlib.decompress(WebContent, 16+zlib.MAX_WBITS)
		# else :
		# 	html = WebContent
		# result = chardet.detect(html)
		# writeFile(GET_HTML,html)
		# exit()

		ret = WebContent.find(checkString)

		print '==================='

		#for check get html
		#if ret == -1 :
		#	print '%s Can\'t buy' % webName
		#	filename = 'nobuy_%d.html' % mIndex
		#	writeFile(filename,WebContent)
		#else :
		#	print '%s Buy it !' % webName
		#	sendMail(webName,response.geturl())
		#	checkWeb[2] = '#'
		#	writeFile(GET_HTML,WebContent)

		if ret != -1 :
			print '%s Buy it !' % webName
			sendMail(webName,response.geturl())
			checkWeb[2] = '#'
			writeFile(GET_HTML,WebContent)
		else :
			print '%s Can\'t buy' % webName
			filename = 'nobuy_%d.html' % mIndex
			writeFile(filename,WebContent)

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

if __name__ == '__main__' :
	start()
