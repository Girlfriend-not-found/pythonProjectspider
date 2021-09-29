import requests
import base64
import yaml
import sys
import os
import ddddocr
import onnxruntime
from pyDes import des, CBC, PAD_PKCS5
from datetime import datetime, timedelta, timezone

onnxruntime.set_default_logger_severity(3)

with open('./config.yml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def generator(path):
    onnxruntime.set_default_logger_severity(3)
    with open(path, 'rb') as f:
        img_bytes = f.read()
    ocr = ddddocr.DdddOcr()
    code = ocr.classification(img_bytes)
    os.remove(path)
    return code

def log(content):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    print(bj_dt.strftime("%Y-%m-%d %H:%M:%S") + ' ' + str(content))
    sys.stdout.flush()

stu_id = str(config['userid'])
stu_password = config['userpassword'].encode()


def des_cbc_encrypt_text(decrypt_text: str, key: str, iv: str) -> str:
    des_obj = des(key[:8].encode('utf-8'), CBC, iv.encode('utf-8'), pad=None, padmode=PAD_PKCS5)
    encrypt_text = des_obj.encrypt(decrypt_text)
    encrypt_text = str(base64.encodebytes(encrypt_text), encoding='utf-8').replace("\n", "")
    return encrypt_text

def get_code(sessions):
    log('开始识别验证码')
    header_code = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
        'Referer': 'http://10.100.0.121:8020/UI/login.html'
    }
    url = 'http://10.100.0.121:8020/public/login/VerifyCode.aspx?'
    request = sessions.get(url, headers=header_code)
    path = './image/code.jpg'
    with open(path, 'wb')as code_img:
        code_img.write(request.content)
    code = generator(path)
    log('验证码识别成功')
    return code

def login():
    log('开始模拟登录')
    sessions = requests.Session()
    sessions.get('http://10.100.0.121:8020/UI/login.html')
    pwd2b64 = base64.b64encode(stu_password).decode()
    code = get_code(sessions)
    data = "{username:'" + stu_id + "',password:'" + pwd2b64 + "',checkcode:'" + code + "',isWeiXin:'0',isSSO:'undefined'}"
    key = '31113001'
    enc = des_cbc_encrypt_text(data, key, key)
    data = {
        'nr': enc
    }
    url = 'http://10.100.0.121:8020/UI/wxInterface/syjx.asmx/Login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
    }

    proxies = {
	    'http': 'http://127.0.0.1:8080',
	}
    
    res = sessions.post(url=url, headers=headers, json=data, proxies=proxies)
    
    if res.text.find('登陆成功')!=-1:
        log('模拟登录成功')
        cookies = sessions.cookies.get_dict()
        print(cookies)
        return cookies
    elif res.text.find('用户名或密码错误')!=-1:
        log('登陆失败，用户名或密码错误，请检查后重新登录！')
        exit(1)
    elif res.text.find('验证码过期')!=-1:
        log('验证码识别错误，请重新登录')
        exit(1)
    else:
        log('未知错误：'+res.json()['d'])
        exit(1)
    

if __name__ == '__main__':
    login()
