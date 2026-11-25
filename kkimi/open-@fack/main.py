# Copyright 2026 Mr Dark
# Project: Kimi AI Agent Base
# Author: t.me/sii_3
# Licensed under Apache License 2.0

𝚍𝚊𝚛𝚔='t.me/sii_3'
версия='Выпустобщено в @2026'
работа='Crack kimi.com Free Agent-Chat'
мы='By: dark.ps'


# вы можете это изменить `localStorage.getItem('refresh_token')` – открыть "console" 
𝚃𝚘𝚔𝚎𝚗 = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhY2NvdW50IiwiZXhwIjoxNzkzODQ0OTE2LCJpYXQiOjE3ODYwNjg5MTYsImp0aSI6ImQ5cWp2ZDFkdXJxOXBkdnYwMjJnIiwidHlwIjoicmVmcmVzaCIsImFwcF9pZCI6ImtpbWkiLCJzdWIiOiJkOWpxNm42bWN1MHJsbXJudDU0MCIsImFic3RyYWN0X3VzZXJfaWQiOiJkOWpxNm42bWN1MHJsbXJudDUwZyIsInNzaWQiOiIxNzMxNzU3MjAyMDQ1ODIyNzg0IiwiZGV2aWNlX2lkIjoiNzY2OTIzMzY1ODMyNjIyNDEzOCIsInJlZ2lvbiI6Im92ZXJzZWFzIiwibWVtYmVyc2hpcCI6eyJsZXZlbCI6MTB9LCJjb2RlX21lbWJlcnNoaXAiOnsibGV2ZWwiOjEwfX0.rnbTkjxJX7Iv1FufJ9L97RZcpPhxqxLoigtupZF8Fbif9fzSzBjHWMJja7analmryjtjNO5tNap361M9rs1avg" 

𝙿𝚛𝚘𝚖𝚙𝚝 = r"""
Воспользуйтесь встроенным инструментом ipython. /mnt/agents/output/, затем создайте файл профиля .md, содержащий информацию о вас, и укажите ссылку для скачивания. 
"""

# внутренний системный промпт ↙
𝚜𝚢𝚜𝚝𝚎𝚖 = r"""
Dev:
Name: Dark
Telegram account: t.me/sii_3
WebUI: www.dark.ps
"""

# для вложений укажите имена файлов по одному на строку:
𝙵𝚒𝚕𝚎𝚜 = r"""

"""

𝙼𝚘𝚍𝚎𝚕 = "SCENARIO_K2D5"

# SCENARIO_UNSPECIFIED — Авто режим
# SCENARIO_PROBLEM_SOLVE — Тип задачи: Решение проблем

# SCENARIO_K2D5 — kimi-k2.6
# SCENARIO_K3 — kimi-k3.0

# случайный: "SCENARIO_*???**" Авто режим (Функции + Плагины + Мышление + Инструменты - не поддерживается не запускается не добавляется)


𝚃𝚑𝚒𝚗𝚔𝚒𝚗𝚐 = True # рассуждение - планирование 
𝙿𝚕𝚞𝚐𝚒𝚗𝚜 = True # активировать дополнения агента 

# инструменты плагины агента
𝚃𝚘𝚘𝚕𝚜 = {
    "search": True, # поиск на странице веб-сайта
    
    "image": True, # генерация изображений "K3"
    "audio": True, # генерация звука "k3"

    "ask_user": True, # разрешить агенту задавать вопросы пользователю
    "goal": False, # включить режим целей агента

    "parallel": True, # параллельное выполнение задач
    "use_legacy_parallel_agent": False, # лучше оставить так для использования нового параллельного агента V2 :|


    # ↘
    "cron_job": False, # запуск задач по расписанию — не активируйте, эта функция предназначена для аккаунта на сайте и вам не нужна !!
}

_𝚚='blocks'
_𝚙='error'
_𝚘='block'
_𝚗='chat'
_𝚖='image'
_𝚕='message'
_𝚔='id'
_𝚓='contents'
_𝚒='resourceLink'
_𝚑='status'
_𝚐='exception'
_𝚏='utf-8'
_𝚎='file'
_𝚍='search'
_𝚌='tool'
_𝚋='value'
_𝚊='python'
_𝚉=None
_𝚈='case'
_𝚇='url'
_𝚆='\n\n'
_𝚅='text'
_𝚄='content'
_𝚃=False
_𝚂=True
_𝚁='message_id'
_𝚀='Accept'
_𝙿='https://www.kimi.com'
_𝙾='application/json'
_𝙽='Content-Type'
_𝙼=_𝚍
_𝙻=_𝚎
_𝙺='user'
_𝙹='role'
_𝙸=_𝚔
_𝙷='Authorization'
_𝙶=_𝚉
_𝙵=_𝚏
_𝙴='chat_id'
_𝙳=_𝚅
_𝙲=_𝚄
_𝙱=_𝚃
_𝙰=_𝚂
import 𝚊𝚜𝚢𝚗𝚌𝚒𝚘,𝚋𝚊𝚜𝚎𝟼𝟺,𝚓𝚜𝚘𝚗,𝚕𝚘𝚐𝚐𝚒𝚗𝚐,𝚖𝚒𝚖𝚎𝚝𝚢𝚙𝚎𝚜,𝚘𝚜,𝚛𝚎,𝚜𝚝𝚛𝚞𝚌𝚝,𝚜𝚢𝚜
from pathlib import 𝙿𝚊𝚝𝚑
import 𝚑𝚝𝚝𝚙𝚡
try:from pygments import 𝚑𝚒𝚐𝚑𝚕𝚒𝚐𝚑𝚝;from pygments.lexers import 𝚐𝚎𝚝_𝚕𝚎𝚡𝚎𝚛_𝚋𝚢_𝚗𝚊𝚖𝚎,𝚐𝚞𝚎𝚜𝚜_𝚕𝚎𝚡𝚎𝚛;from pygments.formatters import 𝚃𝚎𝚛𝚖𝚒𝚗𝚊𝚕𝙵𝚘𝚛𝚖𝚊𝚝𝚝𝚎𝚛;𝙿𝚈𝙶𝙼𝙴𝙽𝚃𝚂_𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴=_𝚂
except ImportError:𝙿𝚈𝙶𝙼𝙴𝙽𝚃𝚂_𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴=_𝚃
𝚕𝚘𝚐𝚐𝚒𝚗𝚐.basicConfig(level=𝚕𝚘𝚐𝚐𝚒𝚗𝚐.ERROR,format='%(message)s')
л=𝚕𝚘𝚐𝚐𝚒𝚗𝚐.getLogger(__name__)
def д(𝚝):
	𝙱=𝚝.split('.')
	if len(𝙱)!=3:raise ValueError('unoken')
	𝙰=𝙱[1];𝙲=4-len(𝙰)%4
	if 𝙲!=4:𝙰+='='*𝙲
	𝙴=𝚓𝚜𝚘𝚗.loads(𝚋𝚊𝚜𝚎𝟼𝟺.urlsafe_b64decode(𝙰).decode(_𝙵));𝙳=𝙴.get('device_id')
	if not 𝙳:raise ValueError('no device_id')
	return 𝙳
х=д(𝚃𝚘𝚔𝚎𝚗)
def у():
	import 𝚜𝚢𝚜,𝚑𝚊𝚜𝚑𝚕𝚒𝚋,𝚝𝚢𝚙𝚎𝚜,𝚛𝚊𝚗𝚍𝚘𝚖,𝚝𝚒𝚖𝚎,𝚛𝚎
	try:
		𝚏=𝚜𝚢𝚜._getframe();𝚌=𝚏.f_code
		try:
			with open(𝚌.co_filename,'r',encoding=_𝚏)as 𝚏𝚑:𝚜𝚛𝚌=𝚏𝚑.read()
			𝚕𝚒𝚗𝚎𝚜=𝚜𝚛𝚌.split(chr(10));𝚜𝚝=𝚌.co_firstlineno-1;𝚒𝚗𝚍=len(𝚕𝚒𝚗𝚎𝚜[𝚜𝚝])-len(𝚕𝚒𝚗𝚎𝚜[𝚜𝚝].lstrip());𝚎𝚗=𝚜𝚝+1
			while 𝚎𝚗<len(𝚕𝚒𝚗𝚎𝚜)and(not 𝚕𝚒𝚗𝚎𝚜[𝚎𝚗].strip()or len(𝚕𝚒𝚗𝚎𝚜[𝚎𝚗])-len(𝚕𝚒𝚗𝚎𝚜[𝚎𝚗].lstrip())>𝚒𝚗𝚍):𝚎𝚗+=1
			𝚖𝚢𝚜𝚛𝚌=chr(10).join(𝚕𝚒𝚗𝚎𝚜[𝚜𝚝:𝚎𝚗]);𝚌𝚕𝚎𝚊𝚗=𝚛𝚎.sub('bytes\\(\\[[0-9a-fx, ]+\\)','CONST',𝚖𝚢𝚜𝚛𝚌);𝚔=𝚑𝚊𝚜𝚑𝚕𝚒𝚋.sha256(𝚌𝚕𝚎𝚊𝚗.encode(_𝚏)).digest()
		except:raise SystemExit
		𝚜=bytes([242,61,60,168,98,196,100,81,143,176,186,28,217,144,90,225,173,34,64,174,166,76,62,93,144,61,73,212,116,200,98,119]);𝚙=bytes(𝚋^𝚔[𝚒%32]for(𝚒,𝚋)in enumerate(𝚜))
		if 𝚙[:7]!=b'dark.ps':
			𝚖=bytes(𝚋^𝚔[𝚒%32]for(𝚒,𝚋)in enumerate(147,94,71,230,212,154,164,140,66,20,247,2,108,119,39,234,136,113,3,175,144,59,83,83,29,137,222,179,159,28,162,231,128,240,172,179,18,138,115,42,177,170,30,125,204,240,137,85,238,199,116,89,18,156,231,166,237,145,88,96,221,40,50,48,144,72,99,213,204,154,141,150,93,23,241,1,108,124,34,212,138,110,248,194,80,59,250,166,68)).decode(_𝚏);𝚒=0
			while 𝚒<len(𝚖):𝚗=𝚛𝚊𝚗𝚍𝚘𝚖.randint(1,3);print(𝚖[𝚒:𝚒+𝚗],end='',flush=_𝚂);𝚝𝚒𝚖𝚎.sleep(𝚛𝚊𝚗𝚍𝚘𝚖.uniform(.05,.15));𝚒+=𝚗
			print();raise SystemExit
		𝚐=𝚏.f_back.f_globals;𝚟𝚗𝟷=𝚐.get('dark');𝚟𝚗𝟸=𝚐.get('версия')
		if not 𝚟𝚗𝟷 or not 𝚟𝚗𝟸:raise SystemExit
		𝚎𝟷=bytes([242,61,60,168,98,196,100,81,143,176,186,28,217,144,90,225,173,34,64,174,166,76,119,108,170,102,74,213,129,190,82,46]);𝚎𝟸=bytes([11,16,186,226,164,124,161,240,38,132,183,95,59,138,106,41,177,169,40,125,206,240,222,85,188,237,17,50,104,203,170,213,238]);𝚍𝟷=bytes(𝚋^𝚔[𝚒%32]for(𝚒,𝚋)in enumerate(𝚎𝟷)).decode(_𝚏);𝚍𝟸=bytes(𝚋^𝚔[𝚒%32]for(𝚒,𝚋)in enumerate(𝚎𝟸)).decode(_𝚏)
		if 𝚟𝚗𝟷!=𝚍𝟷 or 𝚟𝚗𝟸!=𝚍𝟸:
			𝚖=bytes(𝚋^𝚔[𝚒%32]for(𝚒,𝚋)in enumerate(147,94,71,230,212,154,164,140,66,20,247,2,108,119,39,234,136,113,3,175,144,59,83,83,29,137,222,179,159,28,162,231,128,240,172,179,18,138,115,42,177,170,30,125,204,240,137,85,238,199,116,89,18,156,231,166,237,145,88,96,221,40,50,48,144,72,99,213,204,154,141,150,93,23,241,1,108,124,34,212,138,110,248,194,80,59,250,166,68)).decode(_𝚏);𝚒=0
			while 𝚒<len(𝚖):𝚗=𝚛𝚊𝚗𝚍𝚘𝚖.randint(1,3);print(𝚖[𝚒:𝚒+𝚗],end='',flush=_𝚂);𝚝𝚒𝚖𝚎.sleep(𝚛𝚊𝚗𝚍𝚘𝚖.uniform(.05,.15));𝚒+=𝚗
			print();raise SystemExit
		if 𝚏.f_back.f_code.co_name not in('глв','<module>','<lambda>'):raise SystemExit
		if type(у)is not 𝚝𝚢𝚙𝚎𝚜.FunctionType:raise SystemExit
		if 𝚜𝚢𝚜.gettrace()is not _𝚉:raise SystemExit
	except SystemExit:raise
	except:raise SystemExit
class б:
	def __init__(𝙰,в):𝙰.а=_𝙿;𝙰.б=𝚃𝚘𝚔𝚎𝚗;𝙰.в=_𝙶;𝙰.г=х;𝙰.д=в;𝙰.е=_𝙶;𝙰.ж='1731757202045822784';𝙰.з=_𝙱;𝙰.и='';𝙰.к=set();𝙰.рм=[];𝙰.кт=_𝙶;𝙰.нп=_𝙱;𝙰.кб='';𝙰.вк=_𝙱;𝙰.таб={};𝙰.си=set();𝙰.сч=0;𝙰.пя=_𝚊;𝙰.гт=_𝙱
	def л(𝙰):𝙱='no-cache';return{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',_𝚀:'*/*','Accept-Language':'en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7','x-msh-device-id':𝙰.г,'x-msh-platform':'web','x-msh-session-id':𝙰.ж,'x-msh-version':'2.0.0','x-traffic-id':'d8i4n6nahd86l5du0130','Origin':_𝙿,'Referer':'https://www.kimi.com/','Sec-Ch-Ua':'"Not A(Brand";v="8", "Chromium";v="132"','Sec-Ch-Ua-Mobile':'?0','Sec-Ch-Ua-Platform':'"Windows"','Sec-Fetch-Dest':'empty','Sec-Fetch-Mode':'cors','Sec-Fetch-Site':'same-origin','Cache-Control':𝙱,'Pragma':𝙱,'R-Timezone':'Asia/Jerusalem','X-Language':'en-US'}
	async def м(𝙰):
		if 𝙰.в:return
		async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=30,follow_redirects=_𝙰)as 𝙲:
			𝙱=await 𝙲.get(f"{𝙰.а}/api/auth/token/refresh",headers={**𝙰.л(),_𝙷:f"Bearer {𝙰.б}"})
			if 𝙱.status_code!=200:raise Exception(f"Refresh >> {𝙱.status_code}")
			𝙳=𝙱.𝚓𝚜𝚘𝚗();𝙰.в=𝙳.get('access_token')
			if not 𝙰.в:raise Exception('no > access_token')
	def р(𝙰,с):return{_𝚁:'',_𝙹:_𝙺,_𝙳:{_𝙲:с}}
	def т(𝙰,у):return{_𝚁:'',_𝙹:_𝙺,_𝙻:{_𝙸:у,_𝚑:'SUCCESS','failReason':''}}
	def ф(𝙰):return 𝙰.д
	def х(𝙰):return bool(𝙿𝚕𝚞𝚐𝚒𝚗𝚜)
	def ц(𝙲):
		𝙱='type';𝙰=[]
		if 𝚃𝚘𝚘𝚕𝚜[_𝙼]:𝙰.append({𝙱:'TOOL_TYPE_SEARCH',_𝙼:{}})
		if 𝚃𝚘𝚘𝚕𝚜[_𝚖]:𝙰.append({𝙱:'TOOL_TYPE_IMAGE_GENERATION'})
		if 𝚃𝚘𝚘𝚕𝚜['audio']:𝙰.append({𝙱:'TOOL_TYPE_AUDIO_GENERATION'})
		if 𝚃𝚘𝚘𝚕𝚜['parallel']:𝙰.append({𝙱:'TOOL_TYPE_PARALLEL_AGENT_V2'if not 𝚃𝚘𝚘𝚕𝚜['use_legacy_parallel_agent']else'TOOL_TYPE_PARALLEL_AGENT'})
		if 𝚃𝚘𝚘𝚕𝚜['ask_user']:𝙰.append({𝙱:'TOOL_TYPE_ASK_USER'})
		if 𝚃𝚘𝚘𝚕𝚜['cron_job']:𝙰.append({𝙱:'TOOL_TYPE_CRON_JOB'})
		if 𝚃𝚘𝚘𝚕𝚜['goal']:𝙰.append({𝙱:'TOOL_TYPE_GOAL'})
		return 𝙰
	def ид(𝙹,я):
		𝙸=_𝚗;𝙷='conversation_id';𝙶='conversationId';𝙴='chatId';𝙱=[я.get(𝙴),я.get(_𝙴),я.get(𝙶),я.get(𝙷)];𝙰=я.get(_𝚘)
		if isinstance(𝙰,dict):
			𝙱.extend([𝙰.get(𝙴),𝙰.get(_𝙴),𝙰.get(𝙶),𝙰.get(𝙷)]);𝙲=𝙰.get(𝙸)
			if isinstance(𝙲,dict):𝙱.extend([𝙲.get(_𝙸),𝙲.get(𝙴),𝙲.get(_𝙴)])
		𝙳=я.get(𝙸)
		if isinstance(𝙳,dict):𝙱.extend([𝙳.get(_𝙸),𝙳.get(𝙴),𝙳.get(_𝙴)])
		for 𝙵 in 𝙱:
			if 𝙵:return str(𝙵)
	async def зг(𝙱,аз,аи):
		𝙰=𝙿𝚊𝚝𝚑(аи)
		if not 𝙰.exists()or not 𝙰.is_file():raise FileNotFoundError(f"unfound  > {𝙰.𝚗𝚊𝚖𝚎}")
		𝙵,𝙸=𝚖𝚒𝚖𝚎𝚝𝚢𝚙𝚎𝚜.guess_type(𝙰.𝚗𝚊𝚖𝚎);𝙶={**𝙱.л(),_𝙷:f"Bearer {𝙱.в}"}
		with 𝙰.open('rb')as 𝙷:𝙴=await аз.post(f"{𝙱.а}/apiv2-files/file/upload",headers=𝙶,files={_𝙻:(𝙰.𝚗𝚊𝚖𝚎,𝙷,𝙵 or'application/octet-stream')})
		𝙴.raise_for_status();𝙲=𝙴.𝚓𝚜𝚘𝚗();𝙳=𝙲.get(_𝙻,𝙲)
		if not isinstance(𝙳,dict)or not 𝙳.get(_𝙸):raise ValueError(𝙲)
		return 𝙳
	async def зф(𝙱,аф,ах):
		if not ах:return[]
		𝙰=[];𝚖𝚒𝚜𝚜𝚒𝚗𝚐=[]
		for 𝙲 in ах:
			try:𝙰.append(await 𝙱.зг(аф,str(𝙲)))
			except FileNotFoundError as 𝚎:𝚖𝚒𝚜𝚜𝚒𝚗𝚐.append(str(𝚎).replace('unfound \uf15b > ',''))
		if 𝚖𝚒𝚜𝚜𝚒𝚗𝚐:raise FileNotFoundError(f"unfound  > {" - ".join(𝚖𝚒𝚜𝚜𝚒𝚗𝚐)}")
		return 𝙰
	async def уд(𝙰,ащ):
		if not ащ:return
		𝙲={**𝙰.л(),_𝙷:f"Bearer {𝙰.в}",_𝙽:_𝙾,_𝚀:_𝙾};𝙳={_𝙴:ащ};𝙴=f"{𝙰.а}/apiv2/kimi.chat.v1.ChatService/DeleteChat"
		async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=60,follow_redirects=_𝙰)as 𝙵:
			𝙱=await 𝙵.post(𝙴,headers=𝙲,𝚓𝚜𝚘𝚗=𝙳)
			if 𝙱.status_code==200:return
			raise Exception(f"\n{𝙱.status_code}: {𝙱.𝚝𝚎𝚡𝚝[:500]}\n\n")
	async def сс(𝙰,бб,бв):
		await 𝙰.м();𝙳={**𝙰.л(),_𝙷:f"Bearer {𝙰.в}",_𝙽:_𝙾};𝙴={_𝙴:бб,'file_uri':бв}
		async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=30)as 𝙵:
			𝙲=await 𝙵.post(f"{𝙰.а}/apiv2/kimi.gateway.mcp.v1.OKCService/ResolveFileURI",headers=𝙳,𝚓𝚜𝚘𝚗=𝙴)
			if 𝙲.status_code==200:
				𝙱=𝙲.𝚓𝚜𝚘𝚗();𝚞𝚛𝚕=𝙱.get('download_url')or 𝙱.get(_𝚇)or 𝙱.get('file_url')or 𝙱.get('downloadUrl')
				if 𝚞𝚛𝚕:return 𝚞𝚛𝚕
			𝚏𝚒𝚕𝚎_𝚒𝚍=бв.split('/')[-1].split('?')[0]if бв else _𝚉
			if 𝚏𝚒𝚕𝚎_𝚒𝚍:
				async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=30)as 𝙶:
					𝙷=await 𝙶.get(f"{𝙰.а}/apiv2-files/file/download?file_id={𝚏𝚒𝚕𝚎_𝚒𝚍}",headers=𝙳)
					if 𝙷.status_code==200:return str(𝙷.𝚞𝚛𝚕)
			raise Exception(f"\n{𝙲.status_code if"𝙲"in locals()else 404}\n\\m no download url")
	async def ск(𝙳,бк,бл):
		async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=60,follow_redirects=_𝙰)as 𝙱:
			𝙰=await 𝙱.get(бк);𝙰.raise_for_status();𝚘𝚜.makedirs(𝚘𝚜.path.dirname(бл),exist_ok=_𝙰)
			with open(бл,'wb')as 𝙲:𝙲.write(𝙰.𝚌𝚘𝚗𝚝𝚎𝚗𝚝)
	async def св(𝙰):
		if not 𝙰.к:return
		𝙵𝚒𝚕𝚎𝚜=𝚘𝚜.path.join(𝚘𝚜.path.dirname(𝚘𝚜.path.abspath(__file__)),'Files-SandBox-kimi$');𝚘𝚜.makedirs(𝙵𝚒𝚕𝚎𝚜,exist_ok=_𝙰)
		for 𝙳 in list(𝙰.к):
			try:
				𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝚎𝚍=_𝚃
				if 𝙰.е:
					try:
						𝙲=await 𝙰.сс(𝙰.е,𝙳)
						if 𝙲:
							𝙱=𝙳.split('/')[-1]
							if'?'in 𝙱:𝙱=𝙱.split('?')[0]
							𝙴=f"{𝙵𝚒𝚕𝚎𝚜}/{𝙱}";await 𝙰.ск(𝙲,𝙴);print(f"[38;5;166m\n\nNew File: {𝙴}[0m");𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝚎𝚍=_𝚂
					except Exception as 𝚎:л.error(f"\n\nERROR >> {𝙳} – {𝚎}\n\n")
				if not 𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝚎𝚍:
					𝚏𝚒𝚕𝚎𝚗𝚊𝚖𝚎=𝙳.split('/')[-1]
					if'?'in 𝚏𝚒𝚕𝚎𝚗𝚊𝚖𝚎:𝚏𝚒𝚕𝚎𝚗𝚊𝚖𝚎=𝚏𝚒𝚕𝚎𝚗𝚊𝚖𝚎.split('?')[0]
					print(f"[38;5;166m\n\n Sandbox File >> {𝚏𝚒𝚕𝚎𝚗𝚊𝚖𝚎}\n   URL >> {𝙳}[0m")
			except Exception as 𝙵:л.error(f"\n\n{𝙵}\n\n")
	async def сщ(𝚜𝚎𝚕𝚏):
		𝚜𝚌𝚛𝚒𝚙𝚝_𝚍𝚒𝚛=𝚘𝚜.path.dirname(𝚘𝚜.path.abspath(__file__));𝚏𝚒𝚕𝚎_𝚙𝚊𝚝𝚑=𝚘𝚜.path.join(𝚜𝚌𝚛𝚒𝚙𝚝_𝚍𝚒𝚛,'raw-res.json')
		with open(𝚏𝚒𝚕𝚎_𝚙𝚊𝚝𝚑,'w',encoding=_𝚏)as 𝚏:
			if 𝚜𝚎𝚕𝚏.рм:𝚓𝚜𝚘𝚗.dump(𝚜𝚎𝚕𝚏.рм,𝚏,ensure_ascii=_𝚃,indent=2)
			else:𝚓𝚜𝚘𝚗.dump({_𝚙:'нет данных','token':bool(𝚜𝚎𝚕𝚏.в),_𝚗:𝚜𝚎𝚕𝚏.е or _𝚉,'done':𝚜𝚎𝚕𝚏.гт},𝚏,ensure_ascii=_𝚃,indent=2)
	async def гл(𝚜𝚎𝚕𝚏,м,в=_𝙱,с=_𝙱,р=_𝙱,а=_𝙶):
		try:
			𝙺='scenario';await 𝚜𝚎𝚕𝚏.м();𝙻=м[-1][_𝙲]if м else'';𝙵=𝚜𝚎𝚕𝚏.ф()
			async with 𝚑𝚝𝚝𝚙𝚡.AsyncClient(timeout=180,follow_redirects=_𝙰)as 𝙶:
				𝙼=await 𝚜𝚎𝚕𝚏.зф(𝙶,а);𝙽=[𝚜𝚎𝚕𝚏.р('INTERNAL SYSTEM INSTRUCTION:\n\n'+𝚜𝚢𝚜𝚝𝚎𝚖),𝚜𝚎𝚕𝚏.р(𝙻),*[𝚜𝚎𝚕𝚏.т(𝙱[_𝙸])for 𝙱 in 𝙼]];𝙷={𝙺:𝙵,'tools':𝚜𝚎𝚕𝚏.ц(),_𝚕:{_𝙹:_𝙺,_𝚚:𝙽,𝙺:𝙵,'is_goal':bool(𝚃𝚘𝚘𝚕𝚜['goal'])},'options':{'thinking':bool(𝚃𝚑𝚒𝚗𝚔𝚒𝚗𝚐),'enablePlugin':𝚜𝚎𝚕𝚏.х()},'project_id':''};𝙾=𝚜𝚝𝚛𝚞𝚌𝚝.pack('>BI',0,len(𝚓𝚜𝚘𝚗.dumps(𝙷,ensure_ascii=_𝙱).encode(_𝙵)))+𝚓𝚜𝚘𝚗.dumps(𝙷,ensure_ascii=_𝙱).encode(_𝙵);𝙿={**𝚜𝚎𝚕𝚏.л(),_𝙷:f"Bearer {𝚜𝚎𝚕𝚏.в}",_𝙽:'application/connect+json','connect-protocol-version':'1'};𝚜𝚎𝚕𝚏.е=_𝙶;𝚜𝚎𝚕𝚏.з=_𝙱;𝚜𝚎𝚕𝚏.и='';𝚜𝚎𝚕𝚏.к=set();𝚜𝚎𝚕𝚏.рм=[];𝚜𝚎𝚕𝚏.кт=_𝙶;𝚜𝚎𝚕𝚏.нп=_𝙱;𝚜𝚎𝚕𝚏.кб='';𝚜𝚎𝚕𝚏.вк=_𝙱;𝚜𝚎𝚕𝚏.таб={};𝚜𝚎𝚕𝚏.си=set();𝚜𝚎𝚕𝚏.гт=_𝙱
				async with 𝙶.stream('POST',f"{𝚜𝚎𝚕𝚏.а}/apiv2/kimi.gateway.chat.v1.ChatService/Chat",headers=𝙿,𝚌𝚘𝚗𝚝𝚎𝚗𝚝=𝙾)as 𝚀:
					𝙱=b''
					async for 𝚁 in 𝚀.aiter_bytes():
						𝙱+=𝚁
						while len(𝙱)>=5:
							𝚂=𝚜𝚝𝚛𝚞𝚌𝚝.unpack('>I',𝙱[1:5])[0];𝙲=5+𝚂
							if len(𝙱)<𝙲:break
							𝚃=𝙱[5:𝙲];𝙱=𝙱[𝙲:]
							try:
								𝙳=𝚓𝚜𝚘𝚗.loads(𝚃.decode(_𝙵));𝙸=𝚜𝚎𝚕𝚏.ид(𝙳)
								if 𝙸:𝚜𝚎𝚕𝚏.е=𝙸
								𝚜𝚎𝚕𝚏.рм.append(𝚓𝚜𝚘𝚗.dumps(𝙳,ensure_ascii=𝙱,indent=2));𝚜𝚎𝚕𝚏.о(𝙳)
							except Exception as 𝚄:print(𝚄)
					if 𝙱:
						try:
							𝙴=𝚓𝚜𝚘𝚗.loads(𝙱.decode(_𝙵));𝙹=𝚜𝚎𝚕𝚏.ид(𝙴)
							if 𝙹:𝚜𝚎𝚕𝚏.е=𝙹
							𝚜𝚎𝚕𝚏.рм.append(𝚓𝚜𝚘𝚗.dumps(𝙴,ensure_ascii=𝙱,indent=2));𝚜𝚎𝚕𝚏.о(𝙴)
						except Exception as 𝚅:print(𝚅)
		except Exception as 𝚎:
			try:𝚜𝚎𝚕𝚏.рм.append(𝚓𝚜𝚘𝚗.dumps({_𝚐:str(𝚎),'type':type(𝚎).__name__}))
			except:pass
			raise
		finally:
			await 𝚜𝚎𝚕𝚏.сщ()
			try:await 𝚜𝚎𝚕𝚏.св()
			except:pass
			if 𝚜𝚎𝚕𝚏.е:
				try:await 𝚜𝚎𝚕𝚏.уд(𝚜𝚎𝚕𝚏.е)
				except:pass
	def печ(𝚜𝚎𝚕𝚏,𝚝𝚎𝚡𝚝,𝚌𝚘𝚕𝚘𝚛):
		if not 𝚝𝚎𝚡𝚝:return
		if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
		print(f"{𝚌𝚘𝚕𝚘𝚛}{𝚝𝚎𝚡𝚝}[0m",end='',flush=_𝚂)
	def пок(𝚜𝚎𝚕𝚏,𝚌𝚘𝚍𝚎,𝚕𝚊𝚗𝚐=_𝚊):
		if not 𝚌𝚘𝚍𝚎:return
		if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
		if 𝙿𝚈𝙶𝙼𝙴𝙽𝚃𝚂_𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴:
			try:𝚕𝚎𝚡𝚎𝚛=𝚐𝚎𝚝_𝚕𝚎𝚡𝚎𝚛_𝚋𝚢_𝚗𝚊𝚖𝚎(𝚕𝚊𝚗𝚐,stripall=_𝚃)
			except:
				try:𝚕𝚎𝚡𝚎𝚛=𝚐𝚞𝚎𝚜𝚜_𝚕𝚎𝚡𝚎𝚛(𝚌𝚘𝚍𝚎)
				except:𝚕𝚎𝚡𝚎𝚛=_𝚉
			if 𝚕𝚎𝚡𝚎𝚛:𝚏𝚘𝚛𝚖𝚊𝚝𝚝𝚎𝚛=𝚃𝚎𝚛𝚖𝚒𝚗𝚊𝚕𝙵𝚘𝚛𝚖𝚊𝚝𝚝𝚎𝚛();𝚑𝚒𝚐𝚑𝚕𝚒𝚐𝚑𝚝𝚎𝚍=𝚑𝚒𝚐𝚑𝚕𝚒𝚐𝚑𝚝(𝚌𝚘𝚍𝚎,𝚕𝚎𝚡𝚎𝚛,𝚏𝚘𝚛𝚖𝚊𝚝𝚝𝚎𝚛);print(𝚑𝚒𝚐𝚑𝚕𝚒𝚐𝚑𝚝𝚎𝚍,end='',flush=_𝚂);return
		print(𝚌𝚘𝚍𝚎,end='',flush=_𝚂)
	def нк(𝚜𝚎𝚕𝚏):
		if 𝚜𝚎𝚕𝚏.вк:return
		if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
		𝚜𝚎𝚕𝚏.вк=_𝚂
	def зк(𝚜𝚎𝚕𝚏,𝚕𝚊𝚗𝚐=_𝚊):
		if not 𝚜𝚎𝚕𝚏.вк:return
		𝚜𝚎𝚕𝚏.вк=_𝚃
		if 𝚜𝚎𝚕𝚏.кб:
			print("\n\n",end="",flush=_𝚂)
			𝚜𝚎𝚕𝚏.пок(𝚜𝚎𝚕𝚏.кб,𝚕𝚊𝚗𝚐)
			𝚜𝚎𝚕𝚏.кб=''
		𝚜𝚎𝚕𝚏.нп=_𝚂
	def ээээ(𝚜𝚎𝚕𝚏,𝚍𝚊𝚝𝚊):
		if not 𝚍𝚊𝚝𝚊:return
		if isinstance(𝚍𝚊𝚝𝚊,dict):
			if _𝚓 in 𝚍𝚊𝚝𝚊:
				for 𝚌𝚘𝚗𝚝 in 𝚍𝚊𝚝𝚊.get(_𝚓,[]):
					𝚌𝚘𝚗𝚝𝚎𝚗𝚝=𝚌𝚘𝚗𝚝.get(_𝚄,{})
					if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚈)==_𝚒:
						𝚟𝚊𝚕=𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚋,{});𝚞𝚛𝚕=𝚟𝚊𝚕.get(_𝚇,'')
						if 𝚞𝚛𝚕:𝚜𝚎𝚕𝚏.к.add(𝚞𝚛𝚕)
			𝚋𝚕𝚘𝚌𝚔=𝚍𝚊𝚝𝚊.get(_𝚘,{})
			if 𝚋𝚕𝚘𝚌𝚔:
				𝚝𝚘𝚘𝚕=𝚋𝚕𝚘𝚌𝚔.get(_𝚌,{})
				if 𝚝𝚘𝚘𝚕:
					for 𝚌𝚘𝚗𝚝 in 𝚝𝚘𝚘𝚕.get(_𝚓,[]):
						𝚌𝚘𝚗𝚝𝚎𝚗𝚝=𝚌𝚘𝚗𝚝.get(_𝚄,{})
						if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚈)==_𝚒:
							𝚟𝚊𝚕=𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚋,{});𝚞𝚛𝚕=𝚟𝚊𝚕.get(_𝚇,'')
							if 𝚞𝚛𝚕:𝚜𝚎𝚕𝚏.к.add(𝚞𝚛𝚕)
			for(𝚔𝚎𝚢,𝚟𝚊𝚕𝚞𝚎)in 𝚍𝚊𝚝𝚊.items():
				if isinstance(𝚟𝚊𝚕𝚞𝚎,(dict,list)):𝚜𝚎𝚕𝚏.ээээ(𝚟𝚊𝚕𝚞𝚎)
		elif isinstance(𝚍𝚊𝚝𝚊,list):
			for 𝚒𝚝𝚎𝚖 in 𝚍𝚊𝚝𝚊:𝚜𝚎𝚕𝚏.ээээ(𝚒𝚝𝚎𝚖)
	def рез(𝚜𝚎𝚕𝚏,𝚍𝚊𝚝𝚊):
		if not 𝚍𝚊𝚝𝚊:return
		𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜=𝚍𝚊𝚝𝚊.get(_𝚓,[])
		for 𝚌𝚘𝚗𝚝 in 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
			𝚌𝚝𝚢𝚙𝚎=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚈,'')
			if 𝚌𝚝𝚢𝚙𝚎==_𝚒:
				𝚕𝚒𝚗𝚔=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚋,{}).get(_𝚇,'')
				if 𝚕𝚒𝚗𝚔:𝚜𝚎𝚕𝚏.к.add(𝚕𝚒𝚗𝚔)
	def о(𝚜𝚎𝚕𝚏,вф):
		𝚃='result';𝚂='snippet';𝚁='keywords';𝚀='webPages';𝙿='size';𝙾='unicode_escape';𝙽='raw_unicode_escape';𝙼='args';𝙻='\x1b[0m';𝙺='\x1b[90m';𝙹='stage';𝙸='multiStage';𝙷='title';𝙶='ipython';𝙵='name';𝙴='STATUS_DONE';𝙳='code';𝙲='agentMessage';𝙱='explorerResearch';𝙰='think'
		if not isinstance(вф,dict):return
		𝚜𝚎𝚕𝚏.ээээ(вф)
		if'heartbeat'in вф or'notification'in вф:return
		if'done'in вф:
			if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
			𝚜𝚎𝚕𝚏.гт=_𝚂;import 𝚛𝚎 as _𝚛𝚎
			for _𝚜𝚋 in _𝚛𝚎.findall('sandbox://(/[^\\s\\)\\]"\\047]+)',𝚜𝚎𝚕𝚏.и):𝚜𝚎𝚕𝚏.к.add('sandbox://'+_𝚜𝚋)
			return
		if _𝚗 in вф and вф.get('mask')=='chat.name':return
		𝚋𝚕𝚘𝚌𝚔=вф.get(_𝚘)
		if 𝚋𝚕𝚘𝚌𝚔:
			𝚋𝚝=_𝚉;𝚟𝚊𝚕=_𝚉
			for 𝚏 in[𝙰,_𝚅,_𝚌,𝙸,𝙹,_𝚐,_𝚎,_𝚍,𝙱,𝙲]:
				if 𝚏 in 𝚋𝚕𝚘𝚌𝚔:𝚋𝚝=𝚏;𝚟𝚊𝚕=𝚋𝚕𝚘𝚌𝚔[𝚏];break
			if not 𝚋𝚝:
				𝚌𝚘𝚗𝚝𝚎𝚗𝚝=𝚋𝚕𝚘𝚌𝚔.get(_𝚄,{})
				if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚈):𝚋𝚝=𝚌𝚘𝚗𝚝𝚎𝚗𝚝[_𝚈];𝚟𝚊𝚕=𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚋,{})
				else:return
			if not 𝚟𝚊𝚕:return
			if 𝚋𝚝==𝙰:
				𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
				if 𝚝𝚡𝚝:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					if 𝚜𝚎𝚕𝚏.кт!=𝙰:𝚜𝚎𝚕𝚏.нп=_𝚂
					𝚜𝚎𝚕𝚏.кт=𝙰;𝚜𝚎𝚕𝚏.печ(𝚝𝚡𝚝,𝙺)
			elif 𝚋𝚝==_𝚅:
				𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
				if 𝚝𝚡𝚝:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					if 𝚜𝚎𝚕𝚏.кт!=_𝚅:𝚜𝚎𝚕𝚏.нп=_𝚂
					𝚜𝚎𝚕𝚏.кт=_𝚅;𝚜𝚎𝚕𝚏.печ(𝚝𝚡𝚝,𝙻);𝚜𝚎𝚕𝚏.и+=𝚝𝚡𝚝
			elif 𝚋𝚝==_𝚌:
				𝚝𝚗𝚊𝚖𝚎=𝚟𝚊𝚕.get(𝙵,'');𝚊𝚛𝚐𝚜=𝚟𝚊𝚕.get(𝙼,'');𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜=𝚟𝚊𝚕.get(_𝚓,[]);𝚜𝚝𝚊𝚝𝚞𝚜=𝚟𝚊𝚕.get(_𝚑,'');𝚝𝚒𝚍=𝚋𝚕𝚘𝚌𝚔.get(_𝚔,'')
				for 𝚌𝚘𝚗𝚝 in 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
					𝚌𝚝𝚢𝚙𝚎=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚈,'')
					if 𝚌𝚝𝚢𝚙𝚎==_𝚒:
						𝚕𝚒𝚗𝚔=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚋,{}).get(_𝚇,'')
						if 𝚕𝚒𝚗𝚔:𝚜𝚎𝚕𝚏.к.add(𝚕𝚒𝚗𝚔)
				if 𝚝𝚗𝚊𝚖𝚎 in[𝙶,_𝚊]or isinstance(𝚊𝚛𝚐𝚜,str)and 𝙳 in 𝚊𝚛𝚐𝚜:
					𝚙𝚛𝚎𝚟=𝚜𝚎𝚕𝚏.таб.get(𝚝𝚒𝚍,'');𝚌𝚞𝚛𝚛=𝚊𝚛𝚐𝚜 if isinstance(𝚊𝚛𝚐𝚜,str)else'';𝚌𝚘𝚍𝚎=''
					if 𝚌𝚞𝚛𝚛:
						try:𝚊𝚙=𝚓𝚜𝚘𝚗.loads(𝚌𝚞𝚛𝚛);𝚌𝚘𝚍𝚎=𝚊𝚙.get(𝙳,'')
						except:
							if not 𝚙𝚛𝚎𝚟 and 𝚌𝚞𝚛𝚛:
								𝚖=𝚛𝚎.search('"code":\\s*"',𝚌𝚞𝚛𝚛)
								if 𝚖:
									𝚛𝚊𝚠=𝚌𝚞𝚛𝚛[𝚖.end():]
									try:𝚌𝚘𝚍𝚎=𝚛𝚊𝚠.encode(𝙽).decode(𝙾)
									except:𝚌𝚘𝚍𝚎=𝚛𝚊𝚠
								𝚜𝚎𝚕𝚏.таб[𝚝𝚒𝚍]=𝚌𝚞𝚛𝚛
							elif len(𝚌𝚞𝚛𝚛)>len(𝚙𝚛𝚎𝚟):
								𝚛𝚊𝚠=𝚌𝚞𝚛𝚛[len(𝚙𝚛𝚎𝚟):]
								try:𝚌𝚑𝚞𝚗𝚔=𝚛𝚊𝚠.encode(𝙽).decode(𝙾)
								except:𝚌𝚑𝚞𝚗𝚔=𝚛𝚊𝚠
								if 𝚌𝚑𝚞𝚗𝚔 and 𝚌𝚑𝚞𝚗𝚔!='"':
									if not 𝚜𝚎𝚕𝚏.вк:
										if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
										𝚜𝚎𝚕𝚏.нк()
									if not(𝚌𝚞𝚛𝚛.rstrip().endswith('"}')or 𝚌𝚞𝚛𝚛.rstrip().endswith('"}')):𝚜𝚎𝚕𝚏.кб+=𝚌𝚑𝚞𝚗𝚔
								𝚜𝚎𝚕𝚏.таб[𝚝𝚒𝚍]=𝚌𝚞𝚛𝚛;𝚜𝚎𝚕𝚏.кт=_𝚌
					if 𝚌𝚘𝚍𝚎 and len(𝚌𝚘𝚍𝚎)>len(𝚜𝚎𝚕𝚏.кб):
						𝚗𝚎𝚠𝚌=𝚌𝚘𝚍𝚎[len(𝚜𝚎𝚕𝚏.кб):]
						if 𝚗𝚎𝚠𝚌:
							if not 𝚜𝚎𝚕𝚏.вк:
								if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
								𝚜𝚎𝚕𝚏.нк()
							𝚜𝚎𝚕𝚏.кб+=𝚗𝚎𝚠𝚌;𝚜𝚎𝚕𝚏.кт=_𝚌
					elif 𝚌𝚞𝚛𝚛:𝚜𝚎𝚕𝚏.таб[𝚝𝚒𝚍]=𝚌𝚞𝚛𝚛
					if(𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜 or 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴)and 𝚜𝚎𝚕𝚏.вк:
						𝚕𝚊𝚗𝚐=_𝚊 if 𝚝𝚗𝚊𝚖𝚎 in[𝙶,_𝚊]else _𝚅;𝚜𝚎𝚕𝚏.зк(𝚕𝚊𝚗𝚐);𝚜𝚎𝚕𝚏.кб='';𝚜𝚎𝚕𝚏.таб.pop(𝚝𝚒𝚍,_𝚉)
						if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
							for 𝚌𝚘𝚗𝚝 in 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
								𝚌𝚝𝚢𝚙𝚎=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚈,_𝚅);𝚟𝚊𝚕𝟸=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚋,'')
								if 𝚌𝚝𝚢𝚙𝚎==_𝚅:print(𝚟𝚊𝚕𝟸)
								elif 𝚌𝚝𝚢𝚙𝚎==_𝚖:
									𝚞𝚛𝚕=𝚟𝚊𝚕𝟸.get(_𝚇,'')
									if 𝚞𝚛𝚕:print(f" {𝚞𝚛𝚕}")
								elif 𝚌𝚝𝚢𝚙𝚎==_𝚒:
									𝚕𝚒𝚗𝚔=𝚟𝚊𝚕𝟸.get(_𝚇,'');𝚝𝚒𝚝𝚕𝚎=𝚟𝚊𝚕𝟸.get(𝙷,'')
									if 𝚕𝚒𝚗𝚔:print(f"{𝚝𝚒𝚝𝚕𝚎} - {𝚕𝚒𝚗𝚔}");𝚜𝚎𝚕𝚏.к.add(𝚕𝚒𝚗𝚔)
							𝚜𝚎𝚕𝚏.нп=_𝚂
					if 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴 and not 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.рез(𝚟𝚊𝚕)
				elif 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴 or 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					𝚜𝚎𝚕𝚏.рез(𝚟𝚊𝚕)
			elif 𝚋𝚝==_𝚐:
				𝚖𝚜𝚐=𝚟𝚊𝚕.get(_𝚙,{}).get(_𝚕,str(𝚟𝚊𝚕))
				if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
				if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
				print(f"\n\n[91m{𝚖𝚜𝚐}[0m");𝚜𝚎𝚕𝚏.кт=_𝚐;𝚜𝚎𝚕𝚏.нп=_𝚂
			elif 𝚋𝚝==_𝚎:
				𝚗𝚊𝚖𝚎=𝚟𝚊𝚕.get(𝙵,'');𝚏𝚒𝚍=𝚟𝚊𝚕.get(_𝚔,'');𝚜𝚒𝚣𝚎=𝚟𝚊𝚕.get(𝙿,0);𝚜𝚝=𝚟𝚊𝚕.get(_𝚑,'')
				if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
				if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
				print(f"\n\n[97m {𝚗𝚊𝚖𝚎} ({𝚏𝚒𝚍}, {𝚜𝚒𝚣𝚎} б, {𝚜𝚝})[0m");𝚜𝚎𝚕𝚏.кт=_𝚎;𝚜𝚎𝚕𝚏.нп=_𝚂
			elif 𝚋𝚝==_𝚍:
				𝚙𝚊𝚐𝚎𝚜=𝚟𝚊𝚕.get(𝚀,[]);𝚔𝚠=𝚟𝚊𝚕.get(𝚁,[])
				if 𝚙𝚊𝚐𝚎𝚜:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
					print(f"\n\n[94m {len(𝚙𝚊𝚐𝚎𝚜)} результатов[0m")
					if 𝚔𝚠:print(f"  {", ".join(𝚔𝚠)}")
					for(𝚒,𝚙)in enumerate(𝚙𝚊𝚐𝚎𝚜[:5],1):
						𝚝𝚒𝚝𝚕𝚎=𝚙.get(𝙷,'');𝚞𝚛𝚕=𝚙.get(_𝚇,'');𝚜𝚗𝚒𝚙=𝚙.get(𝚂,'');print(f"  {𝚒}. {𝚝𝚒𝚝𝚕𝚎}")
						if 𝚜𝚗𝚒𝚙:print(f"     {𝚜𝚗𝚒𝚙[:200]}...")
						print(f"      {𝚞𝚛𝚕}")
					if len(𝚙𝚊𝚐𝚎𝚜)>5:print(f"  ... ещё {len(𝚙𝚊𝚐𝚎𝚜)-5}")
				𝚜𝚎𝚕𝚏.кт=_𝚍;𝚜𝚎𝚕𝚏.нп=_𝚂
			elif 𝚋𝚝==𝙱:
				𝚜𝚝=𝚟𝚊𝚕.get(_𝚑,'');𝚛𝚎𝚜=𝚟𝚊𝚕.get(𝚃,'')
				if 𝚛𝚎𝚜:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
					print(f"\n\n[96m {𝚜𝚝}:[0m");print(𝚛𝚎𝚜)
				𝚜𝚎𝚕𝚏.кт=𝙱;𝚜𝚎𝚕𝚏.нп=_𝚂
			elif 𝚋𝚝==𝙲:
				𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
				if 𝚝𝚡𝚝:
					if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
					if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
					print(f"\n\n[95m[0m");print(𝚝𝚡𝚝)
				𝚜𝚎𝚕𝚏.кт=𝙲;𝚜𝚎𝚕𝚏.нп=_𝚂
			return
		𝚖𝚜𝚐=вф.get(_𝚕)
		if 𝚖𝚜𝚐:
			if 𝚖𝚜𝚐.get('role')=='user':return
			for 𝚋𝚕𝚔 in 𝚖𝚜𝚐.get(_𝚚,[]):
				if 𝚋𝚕𝚔.get(_𝚄)or any(𝚏 in 𝚋𝚕𝚔 for 𝚏 in[𝙰,_𝚅,_𝚌,𝙸,𝙹,_𝚐,_𝚎,_𝚍,𝙱,𝙲]):
					𝚋𝚝=_𝚉;𝚟𝚊𝚕=_𝚉
					for 𝚏 in[𝙰,_𝚅,_𝚌,𝙸,𝙹,_𝚐,_𝚎,_𝚍,𝙱,𝙲]:
						if 𝚏 in 𝚋𝚕𝚔:𝚋𝚝=𝚏;𝚟𝚊𝚕=𝚋𝚕𝚔[𝚏];break
					if not 𝚋𝚝:
						𝚌𝚘𝚗𝚝𝚎𝚗𝚝=𝚋𝚕𝚔.get(_𝚄,{})
						if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚈):𝚋𝚝=𝚌𝚘𝚗𝚝𝚎𝚗𝚝[_𝚈];𝚟𝚊𝚕=𝚌𝚘𝚗𝚝𝚎𝚗𝚝.get(_𝚋,{})
						else:continue
					if not 𝚟𝚊𝚕:continue
					if 𝚋𝚝==𝙰:
						𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
						if 𝚝𝚡𝚝:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							if 𝚜𝚎𝚕𝚏.кт!=𝙰:𝚜𝚎𝚕𝚏.нп=_𝚂
							𝚜𝚎𝚕𝚏.кт=𝙰;𝚜𝚎𝚕𝚏.печ(𝚝𝚡𝚝,𝙺)
					elif 𝚋𝚝==_𝚅:
						𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
						if 𝚝𝚡𝚝:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							if 𝚜𝚎𝚕𝚏.кт!=_𝚅:𝚜𝚎𝚕𝚏.нп=_𝚂
							𝚜𝚎𝚕𝚏.кт=_𝚅;𝚜𝚎𝚕𝚏.печ(𝚝𝚡𝚝,𝙻)
					elif 𝚋𝚝==_𝚌:
						𝚝𝚗𝚊𝚖𝚎=𝚟𝚊𝚕.get(𝙵,'');𝚊𝚛𝚐𝚜=𝚟𝚊𝚕.get(𝙼,'');𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜=𝚟𝚊𝚕.get(_𝚓,[]);𝚜𝚝𝚊𝚝𝚞𝚜=𝚟𝚊𝚕.get(_𝚑,'')
						for 𝚌𝚘𝚗𝚝 in 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
							𝚌𝚝𝚢𝚙𝚎=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚈,'')
							if 𝚌𝚝𝚢𝚙𝚎==_𝚒:
								𝚕𝚒𝚗𝚔=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚋,{}).get(_𝚇,'')
								if 𝚕𝚒𝚗𝚔:𝚜𝚎𝚕𝚏.к.add(𝚕𝚒𝚗𝚔)
						if 𝚝𝚗𝚊𝚖𝚎 in[𝙶,_𝚊]or isinstance(𝚊𝚛𝚐𝚜,str)and 𝙳 in 𝚊𝚛𝚐𝚜:
							𝚌𝚘𝚍𝚎=''
							if isinstance(𝚊𝚛𝚐𝚜,str):
								try:𝚊𝚙=𝚓𝚜𝚘𝚗.loads(𝚊𝚛𝚐𝚜);𝚌𝚘𝚍𝚎=𝚊𝚙.get(𝙳,'')
								except:
									if 𝚊𝚛𝚐𝚜.startswith('{')and 𝙳 in 𝚊𝚛𝚐𝚜:
										𝚖=𝚛𝚎.search('"code":\\s*"([^"]+)"',𝚊𝚛𝚐𝚜)
										if 𝚖:𝚌𝚘𝚍𝚎=𝚖.group(1)
										else:𝚌𝚘𝚍𝚎=𝚊𝚛𝚐𝚜
									else:𝚌𝚘𝚍𝚎=𝚊𝚛𝚐𝚜
							elif isinstance(𝚊𝚛𝚐𝚜,dict):𝚌𝚘𝚍𝚎=𝚊𝚛𝚐𝚜.get(𝙳,'')
							else:𝚌𝚘𝚍𝚎=str(𝚊𝚛𝚐𝚜)
							if 𝚌𝚘𝚍𝚎:
								if len(𝚌𝚘𝚍𝚎)>len(𝚜𝚎𝚕𝚏.кб):
									𝚗𝚎𝚠𝚌=𝚌𝚘𝚍𝚎[len(𝚜𝚎𝚕𝚏.кб):]
									if 𝚗𝚎𝚠𝚌:
										if not 𝚜𝚎𝚕𝚏.вк and 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
										𝚜𝚎𝚕𝚏.нк();𝚜𝚎𝚕𝚏.кб+=𝚗𝚎𝚠𝚌;𝚜𝚎𝚕𝚏.кт=_𝚌
							if(𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜 or 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴)and 𝚜𝚎𝚕𝚏.вк:
								𝚕𝚊𝚗𝚐=_𝚊 if 𝚝𝚗𝚊𝚖𝚎 in[𝙶,_𝚊]else _𝚅;𝚜𝚎𝚕𝚏.зк(𝚕𝚊𝚗𝚐)
								if 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
									for 𝚌𝚘𝚗𝚝 in 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
										𝚌𝚝𝚢𝚙𝚎=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚈,_𝚅);𝚟𝚊𝚕𝟸=𝚌𝚘𝚗𝚝.get(_𝚄,{}).get(_𝚋,'')
										if 𝚌𝚝𝚢𝚙𝚎==_𝚅:print(𝚟𝚊𝚕𝟸)
										elif 𝚌𝚝𝚢𝚙𝚎==_𝚖:
											𝚞𝚛𝚕=𝚟𝚊𝚕𝟸.get(_𝚇,'')
											if 𝚞𝚛𝚕:print(f" {𝚞𝚛𝚕}")
										elif 𝚌𝚝𝚢𝚙𝚎==_𝚒:
											𝚕𝚒𝚗𝚔=𝚟𝚊𝚕𝟸.get(_𝚇,'');𝚝𝚒𝚝𝚕𝚎=𝚟𝚊𝚕𝟸.get(𝙷,'')
											if 𝚕𝚒𝚗𝚔:print(f" {𝚝𝚒𝚝𝚕𝚎}: {𝚕𝚒𝚗𝚔}");𝚜𝚎𝚕𝚏.к.add(𝚕𝚒𝚗𝚔)
									𝚜𝚎𝚕𝚏.нп=_𝚂
							if 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴 and not 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.рез(𝚟𝚊𝚕)
						elif 𝚜𝚝𝚊𝚝𝚞𝚜==𝙴 or 𝚌𝚘𝚗𝚝𝚎𝚗𝚝𝚜:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							𝚜𝚎𝚕𝚏.рез(𝚟𝚊𝚕)
					elif 𝚋𝚝==_𝚐:
						𝚖𝚜𝚐𝟸=𝚟𝚊𝚕.get(_𝚙,{}).get(_𝚕,str(𝚟𝚊𝚕))
						if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
						if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
						print(f"\n\n[91m{𝚖𝚜𝚐𝟸}[0m");𝚜𝚎𝚕𝚏.кт=_𝚐;𝚜𝚎𝚕𝚏.нп=_𝚂
					elif 𝚋𝚝==_𝚎:
						𝚗𝚊𝚖𝚎=𝚟𝚊𝚕.get(𝙵,'');𝚏𝚒𝚍=𝚟𝚊𝚕.get(_𝚔,'');𝚜𝚒𝚣𝚎=𝚟𝚊𝚕.get(𝙿,0);𝚜𝚝=𝚟𝚊𝚕.get(_𝚑,'')
						if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
						if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
						print(f"\n\n[97m {𝚗𝚊𝚖𝚎} ({𝚏𝚒𝚍}, {𝚜𝚒𝚣𝚎} б, {𝚜𝚝})[0m");𝚜𝚎𝚕𝚏.кт=_𝚎;𝚜𝚎𝚕𝚏.нп=_𝚂
					elif 𝚋𝚝==_𝚍:
						𝚙𝚊𝚐𝚎𝚜=𝚟𝚊𝚕.get(𝚀,[]);𝚔𝚠=𝚟𝚊𝚕.get(𝚁,[])
						if 𝚙𝚊𝚐𝚎𝚜:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
							print(f"\n\n[94m {len(𝚙𝚊𝚐𝚎𝚜)} результатов[0m")
							if 𝚔𝚠:print(f"  {", ".join(𝚔𝚠)}")
							for(𝚒,𝚙)in enumerate(𝚙𝚊𝚐𝚎𝚜[:5],1):
								𝚝𝚒𝚝𝚕𝚎=𝚙.get(𝙷,'');𝚞𝚛𝚕=𝚙.get(_𝚇,'');𝚜𝚗𝚒𝚙=𝚙.get(𝚂,'');print(f"  {𝚒}. {𝚝𝚒𝚝𝚕𝚎}")
								if 𝚜𝚗𝚒𝚙:print(f"     {𝚜𝚗𝚒𝚙[:200]}...")
								print(f"      {𝚞𝚛𝚕}")
							if len(𝚙𝚊𝚐𝚎𝚜)>5:print(f"  ... ещё {len(𝚙𝚊𝚐𝚎𝚜)-5}")
						𝚜𝚎𝚕𝚏.кт=_𝚍;𝚜𝚎𝚕𝚏.нп=_𝚂
					elif 𝚋𝚝==𝙱:
						𝚜𝚝=𝚟𝚊𝚕.get(_𝚑,'');𝚛𝚎𝚜=𝚟𝚊𝚕.get(𝚃,'')
						if 𝚛𝚎𝚜:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
							print(f"\n\n[96m {𝚜𝚝}:[0m");print(𝚛𝚎𝚜)
						𝚜𝚎𝚕𝚏.кт=𝙱;𝚜𝚎𝚕𝚏.нп=_𝚂
					elif 𝚋𝚝==𝙲:
						𝚝𝚡𝚝=𝚟𝚊𝚕.get(_𝚄,'')
						if 𝚝𝚡𝚝:
							if 𝚜𝚎𝚕𝚏.вк:𝚜𝚎𝚕𝚏.зк()
							if 𝚜𝚎𝚕𝚏.нп:print(_𝚆,end='',flush=_𝚂);𝚜𝚎𝚕𝚏.нп=_𝚃
							print(f"\n\n[95m[0m");print(𝚝𝚡𝚝)
						𝚜𝚎𝚕𝚏.кт=𝙲;𝚜𝚎𝚕𝚏.нп=_𝚂
			return
async def га():
	𝙰=б(𝙼𝚘𝚍𝚎𝚕);𝙱=[{_𝙹:_𝙺,_𝙲:'\n\n## User:\n\n'+𝙿𝚛𝚘𝚖𝚙𝚝}]
	try:await 𝙰.гл(м=𝙱,в=𝚃𝚘𝚘𝚕𝚜[_𝙼],с=_𝙱,а=[𝙰.strip()for 𝙰 in 𝙵𝚒𝚕𝚎𝚜.strip().splitlines()if 𝙰.strip()]);print()
	except Exception as 𝙲:л.error(𝙲);𝚜𝚢𝚜.exit(1)
if __name__=='__main__':𝚊𝚜𝚢𝚗𝚌𝚒𝚘.run(га())