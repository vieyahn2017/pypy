# -*- coding: utf-8 -*- 
# http://blog.csdn.net/wangyutian2011/article/details/7764761

import M2Crypto
from M2Crypto import BIO, RSA, DSA, EVP

"""
M2Crypto.BIO 用于操作IO抽象类型。 
M2Crypto.BN 用于操作大数 
M2Crypto.DH 用于操作Diffie-Hellman key exchange protocol 
M2Crypto.EVP 高级的加密解密接口。与直接使用具体的加密算法不同。使用该接口，可以用相同的编程方式，调用不同的算法处理数据。它包含了对称加密算法与非对称加密算法的支持。 
M2Crypto.EC 椭圆曲线非对称加密算法 
M2Crypto.DSA DSA非对称加密算法 
M2Crypto.RSA RSA非对称加密算法 
M2Crypto.Rand 操作随机数 
M2Crypto.SSL 操作SSL协议 
M2Crypto.X509 操作X509 
"""

# 一、如何使用MD5、SHA1等消息散列算法。 
 #虽然OpenSSL提供了直接操作MD5、SHA1算法以及blowfish等各种对称加密算法的API，但是M2Crypto并没有将其包含进来。不过也好，各种算法都有各自的API，记起来麻烦。通过M2Crypto.EVP，我们仍然可以调用这些算法。下面是一个MD5的例子： 
  
def md5(s): 
    m=EVP.MessageDigest("md5") #在构造函数中传入算法的名字可以选择不同的消息散列算法 
    # m=EVP.MessageDigest("sha1")  #常用的散列算法还有sha1。使用方法与MD5类似，只是构造函数是： 
    m.update(s) 
    return m.digest() #或者m.final() 
  


  
# 二、 使用对称加密算法加密数据。 
  
# 如前所述，我们需要使用EVP.Cipher这个比较抽象的API，而不是具体的算法。与EVP.MessageDigest()类似，EVP.Cipher主要提供四个函数： 
  
# EVP.Cipher.__init__(self, alg, key, iv, op, key_as_bytes=0, d='md5', salt='12345678', i=1, padding=1) 
# EVP.Cipher.update(self, data) 
# EVP.Cipher.final() 
# EVP.Cipher.set_padding(self, padding=1) 

#下面是一段使用blowfish算法将明文"fish is here"加密成密文的函数代码： 
  
def blowfish_encrypt(s, password): 
    out=StringIO() 
    m=EVP.Cipher("bf_ecb", password, "123456", 1, 1, "sha1", "saltsalt", 5, 1) 
    out.write(m.update(s)) 
    out.write(m.final()) 
    return out.getvalue() 


# 三、 生成RSA密钥 
  
# DSA与RSA是比较常用的两种非对称加密算法。他们的使用方法与特性正如他们的名字，基本上大同小异。在OpenSSL内，使用与其它名字一样的结构体来表示这两个算法的密钥。在M2Crypto里，也是如此。只是在M2Crypto里DSA与RSA是两个类，带有签名、验证等方法。 
 # 一般并不构造RSA与DSA类。而使用相应的工厂方法。比如生成RSA密钥： 
  

def genrsa(): #这函数生成一个1024位的RSA密钥，将其转化成PEM格式返回 
    bio=BIO.MemoryBuffer() 
    rsa=RSA.gen_key(1024, 3, lambda *arg:None) 
    rsa.save_key_bio(bio, None) 
    return bio.read_all() 


# 四、生成DSA密钥 
# DSA算法相关的估计是另外的人开发的。API有些不大一样。它首先需要生成参数，然后才能生成密钥。以下是一段代码： 
  

def gendsa(): #这函数生成一个1024位的DSA密钥，将其转化成PEM格式返回 
    bio=BIO.MemoryBuffer() 
    dsa = DSA.gen_params(1024, lambda *arg: None) 
    dsa.gen_key() 
    dsa.save_key_bio(bio,None) 
    return bio.read_all() 



# 五、载入DSA密钥与RSA密钥 
""" 
RSA: 
返回RSA类型： 
load_key(file, callback=util.passphrase_callback) 
load_key_bio(bio, callback=util.passphrase_callback) 
load_key_string(string, callback=util.passphrase_callback) 
返回RSA_pub类型： 
load_pub_key(file) 
load_pub_key_bio(bio) 
  
DSA: 
返回DSA类型： 
load_params(file, callback=util.passphrase_callback) 
load_params_bio(bio, callback=util.passphrase_callback) 
load_key(file, callback=util.passphrase_callback) 
load_key_bio(bio, callback=util.passphrase_callback) 
返回DSA_pub类型： 
load_pub_key(file, callback=util.passphrase_callback) 
load_pub_key_bio(bio, callback=util.passphrase_callback)     
"""


# 六、RSA类型的操作——使用RSA加密、解密、签名、认证；保存RSA密钥 

# 七、一个小型的CA，电子证书。 
from M2Crypto import * 
import time 
#首先读取证书请求文件。 
req_str=file("fish_req.pem", "rb").read() 
req=X509.load_request_string(req_str) #返回一个X509.Request类型代表证书请求文件 
print req.verify(req.get_pubkey()) #首先验证一下，是不是真的是使用它本身的私钥签名的。如果是，返回非0值。如果不是，说明这是一个非法的证书请求文件。 
#接下来载入CA的电子证书。与CA的密钥不一样，CA的电子证书包含了CA的身份信息。CA的电子证书会分发给各个通信节点。 
ca_str=file("ca.pem", "rb").read() 
ca=X509.load_cert_string(ca_str) 
#print ca.check_ca() #可以使用check_ca()方法判断这个证书文件是不是CA。本质是判断它是不是自签名。如果是的话，就返回非0值。如果不是的话就返回0。 
#接下来载入CA的密钥 
cakey_str=file("cakey.pem", "rb").read() 
cakey=EVP.load_key_string(cakey_str, lambda *args:"1234") #一般CA的密钥要加密保存。回调函数返回密码 
#接下来开始生成电子证书 
cert=X509.X509() 
#首先，设定开始生效时间与结束生效时间 
t = long(time.time()) + time.timezone #当前时间，单位是秒 
now = ASN1.ASN1_UTCTIME() #开始生效时间。证书的时间类型不是普通的Python datetime类型。 
now.set_time(t) 
nowPlusYear = ASN1.ASN1_UTCTIME() #结束生效时间 
nowPlusYear.set_time(t + 60 * 60 * 24 * 365) #一年以后。 
cert.set_not_before(now) 
cert.set_not_after(nowPlusYear) 
cert.set_subject(req.get_subject()) #把证书请求附带的身份信息复制过来 
cert.set_issuer(ca.get_subject()) #设置颁发者的身份信息，把CA电子证书内身份信息复制过来 
cert.set_serial_number(2) #序列号是指，CA颁发的第几个电子证书文件 
cert.set_pubkey(req.get_pubkey()) #把证书请求内的公钥复制过来 
cert.sign(cakey, "sha1") #使用CA的秘钥进行签名。 
file("fishcert2.pem", "wb").write(cert.as_pem()) #保存文件。 