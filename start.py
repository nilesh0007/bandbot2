from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import parse
import datetime
import param
import teletoken

from time import sleep, strftime, time

def getDriver():
	chromeOptions = {"debuggerAddress":"127.0.0.1:9222"}
	capabilities = {"chromeOptions":chromeOptions}
	print("Driver initializing...")
	driver = webdriver.Remote("http://127.0.0.1:33333", capabilities)
	return driver

def initLogin(isTest = False):
	driver = getDriver()
	print("Driver initialized.")

	driver.get(param.testchatURL if isTest else param.chatURL)
	print("Get login page completed.")
	driver.implicitly_wait(3)

	driver.find_element_by_css_selector(".uBtn.-icoType.-phone").click()
	print("Get PhonenumberPage completed.")
	driver.implicitly_wait(3)

	Phonenumber = input("전화번호 입력 :")
	driver.find_element_by_id("input_local_phone_number").send_keys(Phonenumber)
	driver.find_element_by_css_selector(".uBtn.-tcType.-confirm").click()
	print("Get PasswordPage completed.")
	driver.implicitly_wait(3)

	Password = input("비밀번호 입력 :")
	driver.find_element_by_id("pw").send_keys(Password)
	driver.find_element_by_css_selector(".uBtn.-tcType.-confirm").click()
	print("Get SMSPage completed.")
	driver.implicitly_wait(8)
	try:
		print(driver.find_element_by_id("hintNumberDiv").text)
		sleep(20)
	except NoSuchElementException:
		pw_band=input("인증번호: ")
		driver.find_element_by_id("code").send_keys(str(pw_band))
		driver.find_element_by_css_selector("button.uBtn.-tcType.-confirm").click();
		print("Driver get completed.")
	

	msgWrite = loadingWait(driver)
	return driver, msgWrite

def loadingWait(driver):
	startsec = time()
	while(True):
		try:
			msgWrite = driver.find_element_by_class_name("commentWrite")
		except:
			if(time() > startsec+20):
				now = datetime.datetime.now()
				print("CHAT LOAD ERROR at " + now.isoformat())
				raise ChatError
				exit()
			continue
		break
	sleep(1)
	print("[" + param.NAME + "] " + param.version + " boot success")
	return msgWrite

def loginRefresh(isTest = False):
	driver = getDriver()
	print("Driver initialized.")
	driver.get(param.testchatURL if isTest else param.chatURL)
	print("Driver get completed.")
	msgWrite = loadingWait(driver)
	driver.implicitly_wait(30)
	if isTest:
		msgWrite.send_keys("[" + param.NAME + "] 새로고침 완료")
		msgWrite.send_keys(Keys.ENTER)
	return driver, msgWrite



def Modules():
	import glob
	import importlib
	mods = []
	commands = []
	modules = glob.glob("bandbot_*.py")
	for module in modules:
		module_name = parse.parse("{}.py",module)
		mod = importlib.import_module(module_name[0])
		mods.append(mod)
		commands.append(mod.command)
	return commands, mods

def bothelp(isWrong, commands):
	if(isWrong):
		return "잘못된 명령어입니다.\n"
	else:
		responseChat = param.version
		responseChat += "\nhttps://github.com/kohs100/bandbot2"
		responseChat += "\n지원되는 명령어 : \n!봇 + "
		for command in commands:
			for com in command:
				responseChat += (", "+com)

		return responseChat + "\n"

def HTMLget(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	chatlist = soup.find_all("span", class_="txt")
	userlist = soup.find_all("button", class_="author")
	return len(chatlist), chatlist, userlist
		
def CommandSel(params, usr_i, commands, mods):
	if paramnum == 1:
		return bothelp(False, commands)

	isCommand = False
	for i in range(0, len(commands)):			#commands = list of module.command(list of commands)
		if params[1] in commands[i]:
			return mods[i].Com(params, usr_i)
			isCommand = True
	if not isCommand:
		return bothelp(True, commands)

def newChat(usr_i, str_i, commands, mods):
	def chatPrint(str_i, msgWrite):
		chats = str_i.split("\n")
		for chat in chats:
			msgWrite.send_keys(chat)
			msgWrite.send_keys(Keys.SHIFT, Keys.ENTER)
		msgWrite.send_keys(Keys.ENTER)
	def sendAlarm(usr_i, str_i):
		alarm_keywords = ["촉수","ㅎㅅㅋ","히사코"]
		for keyword in alarm_keywords:
			if keyword in str_i:
				bot = teletoken.getBot()
				msg = strftime("%H:%M ") + usr_i + " is calling you.\n" + str_i
				teletoken.sendChat(bot, msg)

		alarm_users = ["레몬스타"]
		for keyuser in alarm_users:
			if keyuser == usr_i:
				bot = teletoken.getBot()
				msg = "senpai alert" + strftime("%H:%M ") + str_i
				teletoken.sendChat(bot, msg)


	if str_i[:2] == "!봇":
		params = str_i.split(" ")
		if params[0] == "!봇":
			prefixChat = "[" + param.NAME + "] " + usr_i + "\n"
			responseChat = CommandSel(params, usr_i, commands, mods)
			chatPrint(prefixChat + responseChat, msgWrite)

	sendAlarm(usr_i, str_i)

if __name__ == "__main__":
	timeFlag = int(strftime("%M")) < 30

	driver, msgWrite = initLogin()

	len_chat, i_chat, i_user = HTMLget(driver)
	recent_chat = len(i_chat)

	commands, mods = Modules()

	while(True):
		if (int(strftime("%M")) < 30 and timeFlag) or (int(strftime("%M")) >= 30 and not timeFlag):
			timeFlag = not timeFlag
			driver, msgWrite = loginRefresh(True)

		len_chat, i_chat, i_user = HTMLget(driver)

		for i in range(recent_chat-len_chat,0):
			str_i = i_chat[i].text
			usr_i = i_user[i].text
			print(usr_i + ":" + str_i)

			newChat(usr_i, str_i, commands, mods)

		recent_chat = len_chat

		sleep(0.5)