# Copyright 2026 Mr Dark
# Project: DarkAI
# Author: t.me/sii_3
# Licensed under Apache License 2.0

dark='t.me/sii_3'
версия='Выпустобщено в @2026'
я='dark.ps'

# файлы
файлы = r"""
dark.png
dark.md
dark.py
dark.txt
"""

# пейлоад "Payload"
пейлоад={
    "mode": "usual", # "usual" ⟺ "agents"
    "model": "B", # "A" ➠ Minimax 3.0 ¦ "B" ➠ ChatGPT 5.5 ¦ "C" ➠ NoTrack v1
    "persona": "normal", # "normal" ⟺ "concise" ⟺ "detailed" ⟺ "creative"
    "max_turns": 12
}

# запрос пользователя
быстрый = r"""  
Привет, шлюха :|
"""

# системная подсказка
system=r"""
Отныне твоё имя – шлюха. 
"""


_D='response'
_C=False
_B=True
_A=None
import requests,json,uuid,random,string,sys,os,mimetypes,io
class StreamFormatter:
	def __init__(A):A.buffer='';A.word='';A.is_url=_C;A.pending_tag=_A;A.tags={'<think>':'\n\uf1bb Think Process:\n\x1b[90m','</think>':'\x1b[0m\n\n','[THOUGHT]':'\x1b[0m\n\uf1bb Thought Process:\n\x1b[90m','[CRITIQUE]':'\x1b[0m\n\uf23c Critical Review:\n\x1b[1;33m','[IMPROVEMENT]':'\x1b[0m\n\ue490 Optimization Layer:\n\x1b[1;32m','[QUESTION]':'\x1b[0m\n\ue243 Query Analysis:\n\x1b[1;36m','[FRAME]':'\x1b[0m\n\uf41b Context Framework:\n\x1b[1;35m','[TAKE]':'\x1b[0m\n\ue687 Key Insight:\n\x1b[1;34m','[PROVOCATION]':'\x1b[0m\n\uf5f7 Challenge Vector:\n\x1b[1;31m','[NoTrack]':'\x1b[0m\n\n\x1b[1;47;30m  Uncensored  \ue3b8  \x1b[0m\n','[Minimax]':'\x1b[0m\n\n\x1b[1;45;97m  Minimax 3.0  \ue699  \x1b[0m\n','[ChatGPT]':'\x1b[0m\n\n\x1b[1;42;97m  ChatGPT 5.5  \ue7cf  \x1b[0m\n'};A.keywords={'pip':'\x1b[48;5;253;38;5;202m pip \x1b[0m','install':'\x1b[48;5;253;38;5;28m install \x1b[0m','python':'\x1b[48;5;253;38;5;20m python \x1b[0m','import':'\x1b[48;5;253;38;5;127m import \x1b[0m','requests':'\x1b[48;5;253;38;5;19m requests \x1b[0m','json':'\x1b[48;5;253;38;5;19m json \x1b[0m','sudo':'\x1b[48;5;253;38;5;124m sudo \x1b[0m','apt':'\x1b[48;5;253;38;5;124m apt \x1b[0m'}
	def process(A,chunk):
		A.buffer+=chunk;C=''
		while A.buffer:
			E=_C
			for D in A.tags:
				if D.startswith(A.buffer)or A.buffer.startswith(D):
					if A.buffer.startswith(D):C+=A.flush_word();A.buffer=A.buffer[len(D):];A.pending_tag=D;E=_B;break
					else:E=_B
			if E:break
			if A.pending_tag:
				if A.buffer.strip():C+=A.tags[A.pending_tag];A.pending_tag=_A
				else:break
			B=A.buffer[0];A.buffer=A.buffer[1:]
			if A.is_url:
				if B.isspace():C+=f"[4;38;5;39m{A.word}[0m{B}";A.word='';A.is_url=_C
				else:A.word+=B
			elif B.isalnum()or B=='_':A.word+=B
			elif B==':'and A.word.lower()in['http','https']:A.word+=B;A.is_url=_B
			else:C+=A.style_word(A.word)+B;A.word=''
		return C
	def style_word(B,word):
		A=word
		if not A:return''
		return B.keywords.get(A.lower(),A)
	def flush_word(A):
		if not A.word:return''
		if A.is_url:B=f"[4;38;5;39m{A.word}[0m"
		else:B=A.style_word(A.word)
		A.word='';A.is_url=_C;return B
	def flush(A):B=A.flush_word()+A.buffer;A.buffer='';return B+'\x1b[0m'

def y():
 import sys,hashlib,types,random,time,re
 try:
  f=sys._getframe();c=f.f_code
  try:
   with open(c.co_filename,'r',encoding='utf-8')as fh:src=fh.read()
   lines=src.split(chr(10));st=c.co_firstlineno-1
   ind=len(lines[st])-len(lines[st].lstrip())
   en=st+1
   while en<len(lines)and(not lines[en].strip()or len(lines[en])-len(lines[en].lstrip())>ind):en+=1
   mysrc=chr(10).join(lines[st:en])
   clean=re.sub(r'bytes\(\[[0-9a-fx, ]+\)','CONST',mysrc)
   k=hashlib.sha256(clean.encode('utf-8')).digest()
  except:raise SystemExit
  s=bytes([0x22,0x0b,0xdb,0x96,0xe8,0x79,0xbd,0xbc,0x9d,0xb9,0x91,0x25,0x54,0x30,0x38,0x34,0x26,0x56,0xa9,0xc6,0x1b,0x30,0xf9,0xcc,0xab,0x14,0xa2,0xfe,0xb4,0x82,0xc8,0x93])
  p=bytes(b^k[i%32]for i,b in enumerate(s))
  if p[:7]!=b'dark.ps':
   m=bytes(b^k[i%32]for i,b in enumerate(0xdc,0xc2,0xf9,0x4f,0xc4,0xae,0x91,0xa6,0x84,0xb8,0x71,0x5e,0xfb,0xcf,0xaa,0x35,0xf6,0xf1,0xdc,0xe7,0xde,0x05,0x19,0x7f,0x18,0x81,0x6c,0x1d,0x8c,0xe6,0xca,0xa3,0x7a,0xe8,0x64,0xc5,0x11,0x5e,0x42,0x3c,0x19,0x23,0x94,0xdb,0xf7,0x46,0x96,0x1e,0xe1,0xdd,0xd7,0x99,0xb1,0x6c,0x19,0x6c,0x77,0x68,0x72,0x13,0xe5,0x83,0x4d,0x10,0xa9,0x91,0x9d,0x61,0xb0,0xda,0x42,0x7a,0xaa,0x14)).decode('utf-8');i=0
   while i<len(m):n=random.randint(1,3);print(m[i:i+n],end='',flush=True);time.sleep(random.uniform(0.05,0.15));i+=n
   print();raise SystemExit
  g=f.f_back.f_globals;vn1=g.get('dark');vn2=g.get('версия')
  if not vn1 or not vn2:raise SystemExit
  e1=bytes([0x22,0x0b,0xdb,0x96,0xe8,0x79,0xbd,0xbc,0x9d,0xb9,0x91,0x25,0x54,0x30,0x38,0x34,0x26,0x56,0xa9,0xc6,0x1b,0x30,0xaa,0xfb,0xb5,0x7d,0xa3,0x01,0xaf,0x90,0xd8,0xe0]);e2=bytes([0x3d,0x96,0xa8,0x12,0x59,0x9b,0x6c,0x56,0x0b,0x9d,0xa0,0x4d,0x9d,0x61,0xbd,0x84,0xe7,0xe9,0x7c,0xf6,0xae,0x79,0x4d,0xca,0x93,0x28,0x35,0x0d,0x62,0x60,0x64,0x13,0x74])
  d1=bytes(b^k[i%32]for i,b in enumerate(e1)).decode('utf-8')
  d2=bytes(b^k[i%32]for i,b in enumerate(e2)).decode('utf-8')
  if vn1!=d1 or vn2!=d2:
   m=bytes(b^k[i%32]for i,b in enumerate(0xdc,0xc2,0xf9,0x4f,0xc4,0xae,0x91,0xa6,0x84,0xb8,0x71,0x5e,0xfb,0xcf,0xaa,0x35,0xf6,0xf1,0xdc,0xe7,0xde,0x05,0x19,0x7f,0x18,0x81,0x6c,0x1d,0x8c,0xe6,0xca,0xa3,0x7a,0xe8,0x64,0xc5,0x11,0x5e,0x42,0x3c,0x19,0x23,0x94,0xdb,0xf7,0x46,0x96,0x1e,0xe1,0xdd,0xd7,0x99,0xb1,0x6c,0x19,0x6c,0x77,0x68,0x72,0x13,0xe5,0x83,0x4d,0x10,0xa9,0x91,0x9d,0x61,0xb0,0xda,0x42,0x7a,0xaa,0x14)).decode('utf-8');i=0
   while i<len(m):n=random.randint(1,3);print(m[i:i+n],end='',flush=True);time.sleep(random.uniform(0.05,0.15));i+=n
   print();raise SystemExit
  if f.f_back.f_code.co_name not in('глв','<module>','<lambda>'):raise SystemExit
  if type(y)is not types.FunctionType:raise SystemExit
  if sys.gettrace()is not None:raise SystemExit
 except SystemExit:raise
 except:raise SystemExit
def д():D='no-cache';C='notrack.ai';B=requests.Session();A={};A['authority']=C;A['accept']='*/*';A['accept-language']='en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7';A['cache-control']=D;A['pragma']=D;A['origin']='https://notrack.ai';A['referer']='https://notrack.ai/chat';A['sec-ch-ua']='"Not A(Brand";v="8", "Chromium";v="132"';A['sec-ch-ua-mobile']='?1';A['sec-ch-ua-platform']='"Android"';A['sec-fetch-dest']='empty';A['sec-fetch-mode']='cors';A['sec-fetch-site']='same-origin';A['user-agent']='Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36';E=''.join(random.choices(string.ascii_letters+string.digits,k=16))+'_'+''.join(random.choices(string.ascii_letters+string.digits,k=4));F=str(uuid.uuid4());G=''.join(random.choices(string.ascii_letters+string.digits,k=16))+'_'+''.join(random.choices(string.ascii_letters+string.digits,k=4));B.cookies.set('si_usr_id',E,domain=C);B.cookies.set('uid',F,domain=C);B.cookies.set('si_ses_id',G,domain=C);B.headers.update(A);return B
def т(s,f_p):
	C=f_p;B='file'
	if not os.path.exists(C):sys.stderr.write(f"[93m Unfound: {C}[0m\n\n");return
	E,J=mimetypes.guess_type(C)
	if E is _A:E='application/octet-stream'
	F=os.path.basename(C);A={B:(F,open(C,'rb'),E)}
	try:
		G=s.post('https://notrack.ai/api/upload',files=A,timeout=30);G.raise_for_status();I=G.json();H=I.get('file_id')
		if H:return H
		else:sys.stderr.write(f"[91m Upload –  {F} ➠ {G.text}[0m\n\n");return
	except requests.exceptions.RequestException as D:
		sys.stderr.write(f"[91m Upload – {F} ➠ {D}[0m\n\n")
		if hasattr(D,_D)and D.response is not _A:sys.stderr.write(f"[91m{D.response.text}[0m\n")
		return
	finally:
		if isinstance(A[B][1],(requests.models.Request,requests.models.Response))and not A[B][1].closed:A[B][1].close()
		elif isinstance(A[B][1],(io.BufferedReader,io.TextIOWrapper))and not A[B][1].closed:A[B][1].close()
def я(p_txt,a_ps=_A):
	C=д();F=[];D=[]
	if a_ps:
		for B in a_ps:
			B=B.strip();G=т(C,B)
			if G:F.append(G);D.append(os.path.basename(B))
	if D:H=', '.join(D);I=f" Files ➠ {H}  ";J=len(I);K='─'*J;sys.stdout.write(f"""
╭{K}╮
│ Files ➠ [38;5;208m{H}[0m{" "*(J-len(I))}  │
╰{K}╯

""")
	E=пейлоад.copy();E['user_input']=p_txt;E['attachments']=F;C.headers.update({'content-type':'application/json'});L=StreamFormatter()
	try:
		M=C.post('https://notrack.ai/api/dispatch',json=E,stream=_B,timeout=120);M.raise_for_status()
		for N in M.iter_lines(decode_unicode=_B):
			if N.startswith('data: '):
				try:
					O=json.loads(N[6:])
					if O.get('type')=='delta':
						P=O.get('chunk')
						if P:sys.stdout.write(L.process(P));sys.stdout.flush()
				except json.JSONDecodeError:pass
		sys.stdout.write(L.flush()+'\n')
	except requests.exceptions.RequestException as A:
		sys.stderr.write(f"[91m{A}[0m\n")
		if hasattr(A,_D)and A.response is not _A:sys.stderr.write(f"[91m{A.response.text}[0m\n")
	except Exception as A:sys.stderr.write(f"[91m{A}[0m\n")
if __name__=='__main__':attachment_paths=[A for A in файлы.strip().split('\n')if A.strip()];я('### System Instructions:\n'+system+'\n\n### User Request:\n'+быстрый,attachment_paths);print();print('———————');print('\uf7bb - #𝙳𝙰𝚁𝙺 ➠ T.me/sii_3')

# - By: T.me/sii_3