import itchat
from itchat.content import *
import time
import os

# 准备一个字典，在里面放上所有的信息（msg），方便以后遍历使用。其中key为id
msgRec = {}

# 准备一个获取时间的函数，把它格式化成 2017-08-05 16:36:00 的格式并且返回
def getTime(type = 0):
    if(type == 0):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    elif(type == 1):
        return time.strftime("%Y/%m/%d/%H/%M/%S_", time.localtime(time.time()))

# 首先要注册一下信息，也就是判断一下接收到的信息中有哪些是需要进行处理的
# 在这里先筛选出来能够下载的
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def downloadable(msg):
    msgRec[msg['MsgId']] = msg;

def typeChooser(msg):
    print("Get Message!")
    print(msg.__getitem__)
    msgSavingStr = getTime()
    msgFileName = ""
    msgType = msg['Type']
    # 接收到的信息就放在msg里面，之后可以按需调用
    if msgType == 'Text' or msgType == :
        msgSavingStr += (" " + msg['Text'])
    elif msg['Type'] == 'Picture':
        # 先保存下来呗
        msg['Text'](msg['FileName'])
        # 重命名一下，方便查找
        msgFileName = getTime(1)+'FileName'
        os.rename(msg['FileName'], msgFileName)
        msgSavingStr += (" " + msgFileName)


itchat.auto_login(hotReload=True)
itchat.run()