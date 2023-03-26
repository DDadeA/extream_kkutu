print("라이브러리를 불러오는 중...")
import asyncio
import websockets
import json
import random
import math
import numpy as np
print("성공했습니다.")

#
print("사전을 불러오는 중...")
f = open('./_id_ko.csv', 'r', encoding='utf8')
lines = f.readlines()
f.close()
arr = np.array(lines)
print("성공했습니다.")

#[ [ws1, username1], []... ]
data = [] 

# 0 wait / 1 normal / 2 super
gamemode = 0
history = []

async def getpoint(length):
	return math.ceil(80.0/(math.pow(0.8,(length-5.0)) + 1.0))

async def convert(char):
	convertlist = {"라":"나","락":"낙","란":"난","랄":"날","람":"남","랍":"납","랑":"낭","래":"내","랭":"냉","냑":"약","략":"약","냥":"양","량":"양","녀":"여","려":"여","녁":"역","력":"역","년":"연","련":"연","녈":"열","렬":"열","념":"염","렴":"염","렵":"엽","녕":"영","령":"영","녜":"예","례":"예","로":"노","록":"녹","론":"논","롱":"농","뢰":"뇌","뇨":"요","료":"요","룡":"용","루":"누","뉴":"유","류":"유","뉵":"육","륙":"육","륜":"윤","률":"율","륭":"융","륨":"윰","늄":"윰","륵":"늑","름":"늠","릉":"능","니":"이","리":"이","린":"인","림":"임","립":"입"}
	if char in convertlist:
		return convertlist[char]
	return char

async def isExist(word):
	x = np.where(arr == word+'\n')
	return len(x[0])==1

async def isSameSound(prevWord, Word):
	if await convert(Word[0]) == await convert(prevWord[-1:]):
		return True

	return False

async def startNormalGame():
	print('starting normalgame...')

	#clear all point and words 
	for user in data:
		await re_distribution('{ "type":"resetpoint", "username":"' + user[1] + '"}')
		await re_distribution('{ "type":"clearWord", "username":"' + user[1] + '"}')

	#choose random users in list
	randomuser = random.choice(data)[1]
	#choose random word and append it to history
	randomword = random.choice(arr)[:-1]
	global history
	history.append(randomword)

	await re_distribution('{ "type":"maintimer", "time":"80" }')
	await re_distribution('{ "type":"addWord", "username":"'+ randomuser +'", "text": "' + randomword +'"}')

	global gamemode
	gamemode = 1

async def startSuperGame():
	print('starting supergame...')

	global data

	#clear all point and words 
	for user in data:
		await re_distribution('{ "type":"resetWordLength", "username":"' + user[1] + '"}')
		await re_distribution('{ "type":"clearWord", "username":"' + user[1] + '"}')
		await re_distribution('{ "type":"updateWordLength", "username":"' + user[1] + '"}')

	for i in range(0,len(data)):
		#each user
		_user = data[i][1]
		#choose random word and append it to history
		randomword = random.choice(arr)[:-1]
		global history
		history.append(randomword)
		#send random word
		await re_distribution('{ "type":"addWord", "username":"'+ _user +'", "text": "' + randomword +'"}')
		await re_distribution('{ "type":"updateWordLength", "username":"' + _user + '"}')

	#set live stat to all users
	for i in range(0, len(data)):
		data[i][2] = True

	await re_distribution('{ "type":"startSuperGame"}')

	global gamemode
	gamemode = 2


async def stopGame():
	print('stopping game...')

	await re_distribution('{ "type":"stopSuperGame"}')

	global gamemode
	gamemode = 0


async def handleNormalGame(jsondata):
	if jsondata['type'] == 'fail':
		await re_distribution('{ "type":"subpoint", "username":"'+ jsondata['username'] +'", "point":"'+ str(math.ceil(int(jsondata['point'])/5)) +'"}')
		await re_distribution('{ "type":"userAnimate", "username":"'+ jsondata['username'] +'", "animation":"red", "durationSec":"0.4" }')
		global gamemode
		gamemode = 0
		print('game end')
		return

	if len(jsondata['text']) <= 1: 
		await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
		return

	for word in jsondata['wordlist']:
		global history


		# first letter of text == last letter of word
		if not await isSameSound(word, jsondata['text']):
			await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
			continue

		# dictionary check
		elif not await isExist(jsondata['text']):
			await re_distribution('{ "type":"error", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'은/는 없는 단어입니다."}')
			continue

		# if jsondata['text'] in history => refuse
		elif jsondata['text'] in history:
			await re_distribution('{ "type":"error", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'은/는 사용된 단어입니다."}')
			continue

		# append to history
		history.append(jsondata['text'])


		point = await getpoint(len(jsondata['text']))
		await re_distribution('{ "type":"addpoint", "username":"'+ jsondata['username'] +'", "point": "' + str(point) +'"}')
		await re_distribution('{ "type":"animatedMessage", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
		await re_distribution('{ "type":"removeWord", "username":"'+ jsondata['username'] +'", "text": "' + word +'"}')


		#find next user
		nextuser = ""
		names = await getuserlist()
		for index in range(0, len(names)):
			if names[index] == jsondata['username']:
				try: nextuser = names[index + 1]
				except: nextuser = names[0]
				break

		await re_distribution('{ "type":"addWord", "username":"'+ nextuser +'", "text": "' + jsondata['text'] +'"}')

async def handleSuperGame(jsondata):
	global data
	global gamemode

	# set live to False
	if jsondata['type'] == 'fail':
		for i in range(0,len(data)):
			if data[i][1] == jsondata['username']:
				data[i][2] = False
				await re_distribution('{ "type":"userAnimate", "username":"'+ jsondata['username'] +'", "animation":"red", "durationSec":"1.0" }')
				break
		#if nobody True? => end game
		for user in data:
			if user[2]: break
		else:
			gamemode = 0
			await re_distribution('{ "type":"userAnimate", "username":"'+ jsondata['username'] +'", "animation":"green", "durationSec":"5.0" }')
			await re_distribution('{ "type":"stopSuperGame"}')
		return

	# short -> cut!
	if len(jsondata['text']) <= 1: 
		await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
		return

	# if (sender == itself &and& not False), just message it and return
	for i in range(0,len(data)):
		if data[i][1] == jsondata['username'] and not data[i][2]:
			await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
			return


	for word in jsondata['wordlist']:
		global history

		# first letter of text == last letter of word
		if not await isSameSound(word, jsondata['text']):
			await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
			continue

		# dictionary check
		if not await isExist(jsondata['text']):
			await re_distribution('{ "type":"error", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'은/는 없는 단어입니다."}')
			continue

		# if jsondata['text'] in history => refuse
		if jsondata['text'] in history:
			await re_distribution('{ "type":"error", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'은/는 사용된 단어입니다."}')
			continue

		# append to history
		history.append(jsondata['text'])


		await re_distribution('{ "type":"animatedMessage", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')
		await re_distribution('{ "type":"removeWord", "username":"'+ jsondata['username'] +'", "text": "' + word +'"}')

		#send addWord to all True user
		for user in data:
			if user[2] and not user[1] == jsondata['username']:
				await re_distribution('{ "type":"updateWordLength", "username":"' + user[1] + '"}')
				await re_distribution('{ "type":"addWord", "username":"'+ user[1] +'", "text": "' + jsondata['text'] +'"}')
		break
	else: await re_distribution('{ "type":"message", "username":"'+ jsondata['username'] +'", "text": "' + jsondata['text'] +'"}')


async def runCommand(command):
	if command[0] == "addWord":
		await re_distribution('{ "type":"addWord", "username":"'+ command[1] +'", "text": "' + command[2] +'"}')
	elif command[0] == "removeWord":
		await re_distribution('{ "type":"removeWord", "username":"'+ command[1] +'", "text": "' + command[2] +'"}')
	elif command[0] == "start":
		if command[1] == "normal":
			await startNormalGame()
		elif command[1] == "super":
			await startSuperGame()
	elif command[0] == "stop":
		await stopGame()


async def getuserlist():
	names = []
	for ws in data:
		names.append(ws[1])

	return names


async def re_distribution(message):
	for ws in data:
			await ws[0].send(message)


#HANDLE NEW USER
async def handler(websocket):
	#wait for visit message
	visitmessage = await websocket.recv()

	username = json.loads(visitmessage)["username"]
	print(visitmessage)

	if not gamemode == 0: 
		await websocket.send('{ "type" : "no" }')
		return

	#send visit only to old users
	await re_distribution(visitmessage)

	#add new user to list
	global data
	data.append([websocket, username, False])

	#Send list to new user
	names = await getuserlist()
	await websocket.send(('{ "type":"list", "data":"'+ ",".join(names) +'"}'))
	

	#OPEN CONNECTION WITH USER. RUN UNTIL CLOSE CONNECTION
	while True:
		#wait message / fail => exit
		try:
			message = await websocket.recv()
		except:
			try: data.remove([websocket, username, False])
			except: data.remove([websocket, username, True])

			await re_distribution('{ "type":"exit", "username":"'+ username +'"}')
			break


		jsondata = json.loads(message)

		#is it command?
		if jsondata['type'] == "message" and jsondata['text'].startswith('/'):
			await runCommand(jsondata['text'][1:].split(' '))
		elif gamemode == 1:
			await handleNormalGame(jsondata);
		elif gamemode == 2:
			await handleSuperGame(jsondata);
		else:
			await re_distribution(message)

	print("Disconnected from {username}.".format(username=username))


#RUN HANDLER FOREVER
async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()  # run forever


asyncio.run(main())