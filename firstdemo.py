# -*- coding:gb2312 -*-
from sgmllib import SGMLParser
import urllib2,re
from urllib import urlretrieve
import threading
import time
import shutil
import os

class URLLister(SGMLParser):
    """
    urls:chapter url
    """
    match = ''
    dicurl = {}
    def start_a(self, attrs):
        for k, v in attrs:
            if k == 'href' and re.match(self.match,v):
                self.dicurl[v]=True
                
class IMGLister(SGMLParser):
    search = ''
    dicimg = {}
    def start_img(self, attrs):
        for k, v in attrs:
            if k == 'src' and re.search(self.search,v):
                self.dicimg[v] = True
                
def spider(baseurl,dicurl,filepath):
    g_mutex = threading.Lock() 
    url = ''

    for k in dicurl:
        g_mutex.acquire()
        if dicurl[k]:
            dicurl[k]=False
            url = baseurl + k
            break
        g_mutex.release()  
    if url is not '':    
        content = urllib2.urlopen(url).read()
        res = re.split('/',url)
        lenth = len(res)
        filename = res[lenth-1]
        filepath += filename+'.html'
        try:
            fw = open(filepath,'w')
            fw.write(content)
            print filepath + '文件输出成功'
            fw.close()  
        except IOError, e:
            print e
    time.sleep(1)

def spiderimg(baseurl,dicimg,filepath):
    g_mutex = threading.Lock()
    url = ''
    for k in dicimg:
        g_mutex.acquire()
        if dicimg[k]:
            dicimg[k]=False
            url = baseurl + k
            break
        g_mutex.release()
    if url is not '':
        downfile(url,filepath)
    time.sleep(1)
    
def downfile(netpath,localpath):    
    
    filenamerule = re.compile(r'(?<=\btarget\b=)(.*\..*)$')
    filenameres = re.search(filenamerule, netpath)
    filename = filenameres.group(0)
    
    try:
        urlretrieve(netpath,localpath + filename)
        print localpath + filename + '保存成功'
    except IOError, e:
        print e    

#begin 
url_base = 'http://wiki.woodpecker.org.cn'

print '打开网页...'+url_base+'/moin/WxPythonInAction'
content = urllib2.urlopen(url_base+'/moin/WxPythonInAction').read()

print '开始查找href...'

lister=URLLister()
lister.match = '/moin/WxPythonInAction/Chapter'
lister.feed(content)

listimg = IMGLister()
listimg.match = ''

global dicurl
global dicimg
dicurl = lister.dicurl

global g_mutex

threadpool = []

print '文件保存地址(such as d:\docs)'
filepath = raw_input()

'''
filepathrule = re.compile(r'\\$')
res = re.search(filepathrule,filepath)
if res.group(0):
filepath += '\\'

print filepath
'''

try:        
    os.makedirs(filepath)
    print '文件夹不存在，已创建'
except:
    print '文件夹存在，继续执行'


for k in lister.dicurl:
    th = threading.Thread(target = spider, args = (url_base,dicurl,filepath))
    threadpool.append(th)
    
for th in threadpool:     
    th.start()
for th in threadpool: 
    threading.Thread.join(th)

print '文件下载完成，开始下载图片'

folder = 'images\\'
os.makedirs(filepath + folder)

for k in dicurl:
    
    url = url_base + k
    content = urllib2.urlopen(url).read()
    imglister = IMGLister()
    imglister.search = r'/moin/WxPythonInAction/\bChapter\w+\b\?action=AttachFile\&do=get\&target=(.*\..*)$'
    imglister.feed(content)

    dicimg = imglister.dicimg
    '''
    folderrule = re.compile(r'\bChapter\w+\b')
    for val in dicimg:        
        folderres = re.search(folderrule, val)
        folder = folderres.group(0)
        folder += '\\'
        break
    if not os.path.exists(filepath + folder):
        os.makedirs(filepath + folder)
    '''
    
    threadpool2 = []
    for val in imglister.dicimg:
        th = threading.Thread(target = spiderimg, args = (url_base, dicimg, filepath + folder))
        threadpool2.append(th)
    for th in threadpool2:
        th.start()
    for th in threadpool2:
        threading.Thread.join(th)
    print k 
        
