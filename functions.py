import itchat
from itchat.content import *
import time
import os
import re

# 准备一个字典，在里面放上所有的信息（msg），方便以后遍历使用。其中key为id
msgRec = {}

# 用一个文件记录一下所有收到的信息
def record(timeStr, recordStr):
    recordFile = open("record.fhr", 'a')
    recordFile.write("<record><time>" + timeStr + "</time><string>" + recordStr +
                     "</string></record>\n")
    recordFile.close()

# 准备一个获取时间的函数，把它格式化成 2017-08-05_16-36-00 的格式并且返回
def getTime():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))

# 对不同信息进行处理
def msgDealing(msg, isDownloadable = False):
    try:
        print(msg)
        # 获取时间
        timeStr = getTime()
        # 把消息添加到msgRec里面
        msgRec[msg['MsgId']] = msg;
        # 初始化保存信息的字符串
        msgSavingStr = "<type>" + msg['Type'] + "</type>"

        searingName = msg['FromUserName']
        # 如果是自己发的信息，就搜一下发给谁
        if searingName == itchat.search_friends()['UserName']:
            searingName = msg['ToUserName']
            msgSavingStr += "<to>"
        # 搜一下发消息这个人
        friend = itchat.search_friends(userName=searingName)
        if not friend is None:
            print("Received from friend.")
            # msg中添加这个人的身份信息
            if friend['RemarkName'] is None:
                msgRec[msg['MsgId']]['FromName'] = friend['NickName'] + "（没有备注）"
            else:
                msgRec[msg['MsgId']]['FromName'] = friend['NickName'] + "（备注为\"" + friend['RemarkName'] +"\"）"
            # 要保存的字符串
            msgSavingStr += "<friend><nickname>" + friend['NickName'] + "</nickname><remarkname>" + \
                       friend['RemarkName'] + "</friend>"
        else:
            group = itchat.search_chatrooms(userName=searingName)
            if not group is None:
                print("Received from group.")
                msgRec[msg['MsgId']]['FromName'] = msg['ActualNickName'] + "（在群\"" + group['NickName'] + "\"里）"
                msgSavingStr += "<group>" + group['NickName'] + "<user>" + msg['ActualNickName'] + "</user></group>"
            else:
                print("Received from mp.")
                mp = itchat.search_mps(userName=searingName)
                msgRec[msg['MsgId']]['FromName'] = "公众号：" + mp['NickName']
                msgSavingStr += "<mp>" + mp['NickName'] + "</mp>"
        if searingName == msg['ToUserName']:
            msgRec[msg['MsgId']]['FromName'] = "你自己发给：" + msgRec[msg['MsgId']]['FromName']
            msgSavingStr += "</to>"
        if isDownloadable:
            # 先保存下来文件
            msg['Text'](msg['FileName'])
            # 重命名一下，方便查找
            # msgFileName = friend['NickName'] + "_" + friend['RemarkName'] + "_" + msg['FileName']
            # 不支持中文，所以就不改了
            msgFileName = msg['FileName']
            os.rename(msg['FileName'], msgFileName)
            msgRec[msg['MsgId']]['FileName'] = msgFileName
            msgSavingStr += "<filename>" + msgFileName + "</filename>"
        elif msg['Type'] == 'Text':
            msgSavingStr += "<text>" + msg['Text'] + "</text>"
        elif msg['Type'] == 'Card':
            msgSavingStr += "<card><username>" + msg['RecommendInfo']['UserName'] + \
                            "</username><nickname>" + msg['RecommendInfo']['NickName'] + \
                            "</nickname></card>"
        elif msg['Type'] == 'Map':
            x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*",
                                       msg['OriContent']).group(1, 2, 3)
            if location is None:
                msgSavingStr += "<location><x>" + x.__str__() + "</x><y>" + y.__str__() + "</y></location>"
            else:
                msgSavingStr += "<location><x>" + x.__str__() + "</x><y>" + y.__str__() + "</y><loc>" + location + "</loc></location>"
        elif msg['Type'] == 'Sharing':
            msgSavingStr += "<sharing><text>" + msg['Text'] + "</text><url>" + msg['Url'] +\
                            "</url></sharing>"
        elif msg['Type'] == 'Friends':
            msgSavingStr += "<friends>" + msg['Text'] + "</friends>"

        # 保存到文件里面
        record(timeStr, msgSavingStr)
    except:
        print("Dealing Error!")

# 首先要注册一下信息，也就是判断一下接收到的信息中有哪些是需要进行处理的
# 在这里先筛选出来能够下载的
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True, isGroupChat=False, isMpChat=False)
def downloadable1(msg):
    msgDealing(msg, isDownloadable=True)
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=False, isGroupChat=True, isMpChat=False)
def downloadable2(msg):
    msgDealing(msg, isDownloadable=True)
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=False, isGroupChat=False, isMpChat=True)
def downloadable3(msg):
    msgDealing(msg, isDownloadable=True)

# 纯文本格式
@itchat.msg_register([TEXT, MAP, CARD, SHARING, FRIENDS], isFriendChat=True, isGroupChat=False, isMpChat=False)
def text1(msg):
    msgDealing(msg, isDownloadable=False)
@itchat.msg_register([TEXT, MAP, CARD, SHARING, FRIENDS], isFriendChat=False, isGroupChat=True, isMpChat=False)
def text2(msg):
    msgDealing(msg, isDownloadable=False)
@itchat.msg_register([TEXT, MAP, CARD, SHARING, FRIENDS], isFriendChat=False, isGroupChat=False, isMpChat=True)
def text3(msg):
    msgDealing(msg, isDownloadable=False)

# Note类，也就是说撤回和一些其他的网页版微信不支持的东西
@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=False, isMpChat=False)
def note1(msg):
    noteDeal(msg)
@itchat.msg_register([NOTE], isFriendChat=False, isGroupChat=True, isMpChat=False)
def note2(msg):
    noteDeal(msg)
@itchat.msg_register([NOTE], isFriendChat=False, isGroupChat=False, isMpChat=True)
def note3(msg):
    noteDeal(msg)

def noteDeal(msg):
    print(msg)
    # 判断里面有没有出现replacemsg，如果有的话就说明是撤回
    if re.search(r"<replacemsg>", msg['Content']) != None:
        try:
            print("Recalled!")
            # 把撤回的消息序号返回，但是不是oldmsgid的序号（这个oldmsgid不知道是什么东西）
            oldMsg = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
            sendMsg = msgRec[oldMsg]['FromName'];
            sendMsg += " 撤回了一条 " + msgRec[oldMsg]['Type'] + " 消息："
            if msgRec[oldMsg]['Type'] == "Text" or msgRec[oldMsg]['Type'] == "Friends":
                sendMsg += msgRec[oldMsg]['Text']
                itchat.send(sendMsg, toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "Picture":
                itchat.send(sendMsg, toUserName='filehelper')
                itchat.send_image(msgRec[oldMsg]['FileName'], toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "Video":
                itchat.send(sendMsg, toUserName='filehelper')
                itchat.send_video(msgRec[oldMsg]['FileName'], toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "Recording":
                itchat.send(sendMsg, toUserName='filehelper')
                itchat.send_file(msgRec[oldMsg]['FileName'], toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "File":
                itchat.send(sendMsg, toUserName='filehelper')
                itchat.send_file(msgRec[oldMsg]['FileName'], toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "Card":
                sendMsg += "名字为：" + msgRec[oldMsg]['RecommendInfo']['NickName']
                itchat.send(sendMsg, toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == "Map":
                x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*",
                                 msgRec[oldMsg]['OriContent']).group(1, 2, 3)
                if location is None:
                    sendMsg += " x: " + x.__str__() + " y: " + y.__str__()
                else:
                    sendMsg += " x: " + x.__str__() + " y: " + y.__str__() + " loc: " + location
                itchat.send(sendMsg, toUserName='filehelper')
            elif msgRec[oldMsg]['Type'] == 'Sharing':
                sendMsg += "内容：" + msgRec[oldMsg]['Text'] + "连接：" + msgRec[oldMsg]['Url']
        except:
            print("Error!")
    else:
        # 其实我也不知道除了撤回还有什么别的……抢红包什么的都不支持啊，就直接发出来吧，总之有记录
        itchat.send("不支持的消息", toUserName='filehelper')

itchat.auto_login(hotReload=True)
itchat.run()