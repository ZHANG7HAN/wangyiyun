from requests_html import HTMLSession
import random
import base64,codecs
from Crypto.Cipher import AES
import json
import hashlib
import re
import time
def a(a):
    d="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    c = ""
    for i in range(a):
        e=random.choice(d)
        c+=e
    return c
def AES_encrypt(text, key, iv):#AES加密params
    bs = AES.block_size
    pad=16-len(text)%16
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    text=text+str(pad * chr(pad))     
    encryptor = AES.new(key=bytes(key, encoding='utf-8'), mode=AES.MODE_CBC, iv=bytes(iv, encoding='utf-8'))
    encrypt_aes = encryptor.encrypt(bytes(text, encoding='utf8'))
    encrypt_text = base64.b64encode(encrypt_aes).decode('utf8')
    return encrypt_text
def RSA_encSecKey(i, e, f):#RSA加密encSecKey
    f=int(f,16)
    e=int(e,16)
    #print(e)
    i=int(codecs.encode(i[::-1].encode('utf-8'), 'hex_codec'), 16)
    rs=pow(i,e,f)
    return'{:x}'.format(rs).zfill(256)
def Get_Data(phone,password):
    e='010001'#固定
    f="00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"#固定
    key='0CoJUm6Qyw8W8jud'#公钥
    i=a(16)
    password=hashlib.md5(password.encode()).hexdigest()
    meassage={
        'checkToken': "",
        'csrf_token': "",
        'password': "{0}".format(password),#登录密码通过MD5加密
        'phone': "{0}".format(phone),
        'rememberLogin': "true"
            }
    d=json.dumps(meassage)#加密的数据
    iv='0102030405060708'#偏移量
    entext=AES_encrypt(d,key, iv) 
    params=AES_encrypt(entext,i,iv)
    encSecKey=RSA_encSecKey(i, e, f)
    data={
    'params':'{0}'.format(params.strip('\n')),
    'encSecKey':'{0}'.format(encSecKey)
    }
    son_msg = {
        'csrf_token': "d9d4aa8c46a6eb59119f8d4944b9b9f0",
        'limit': "1000",
        'offset': "0",#单页100，初始页0，本次仅抓取第一页
        'total': "true",
        'type': "0",
        'uid': "1296790289"#个人id，网页直接获取
    }
    son_msg=json.dumps(son_msg)#加密歌曲列表的数据
    entext = AES_encrypt(son_msg, key, iv)
    params = AES_encrypt(entext, i, iv)
    son_data = {
        'params': '{0}'.format(params.strip('\n')),
        'encSecKey': '{0}'.format(encSecKey)
    }
    return (data,son_data)
def GetSongs():
    session=HTMLSession()
    headers={  'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
               'Referer':'https://music.163.com/',
                'Content-Type':'application/x-www-form-urlencoded'
     }
    datas=Get_Data(phone,password)[0]
    url='https://music.163.com/weapi/login/cellphone?csrf_token='
    req=session.post(url,headers=headers,data=datas)#登录账号
    #验证是否登录成功，鸡肋。
    try:
        nickname=re.findall(r'"nickname":"(.+?)",',req.text,re.S)[0]
        print('{0}您好，您的账号已登陆成功，正在获取您的历史听歌信息'.format(nickname))
    except:
        print('账号或密码输入错误，请运行重新输入')
    res=session.post('https://music.163.com/weapi/v1/play/record?csrf_token=d9d4aa8c46a6eb59119f8d4944b9b9f0',headers=headers,data=Get_Data(phone,password)[1]).text
    songs=json.loads(res)
    for song in songs['allData']:
        #print(song)
        time.sleep(0.1)
        playCount=song['playCount']#播放次数
        #print(playCount)
        songName=song['song']['name']#歌曲名
        id=song['song']['id']#歌曲id
        authName=song['song']['ar'][0]['name']#歌手名
        msg=songName+','+authName+','+str(id)+','+str(playCount)
        with open('wangyiSong.csv','a+',encoding='utf-8-sig')as f:
            #print(msg)
            f.write(msg+'\n')
    f.close()
    #给程序增加点趣味性的无意义代码
    name=songs['allData'][0]['song']['name']#听的最多的歌名
    count=songs['allData'][0]['playCount']#次数
    print('数据已获取完毕，您听的最多的歌是 《{0}》，一共听了 {1} 次，看来您真的很喜欢这首歌哦！'.format(name,count))

if __name__ == '__main__':
    phone=input('请输入手机号：\n')
    password=input('请输入登陆密码：\n')
    print('*'*100)
    GetSongs()


    
    
