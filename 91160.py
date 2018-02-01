#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib
import requests
import json
import re
import datetime
import time
import smtplib
from email.mime.text import MIMEText


headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36' }

def getSchId(uid,depid,docid):
    SchId = []
    url = 'https://wxis.91160.com/wxis/sch/main.do?unit_id=%s&dep_id=%s&doc_id=%s&dep_name=%s'%(uid,depid,docid,urllib.quote(department[depid]))
    try:
        response = requests.get(url,headers=headers,timeout=6)
    except:
        return { 'code':1, 'message':u'请求超时' }

    mdata = re.search(r'\{"data":(\[.*\])\}', response.text)

    if mdata:
        msg = json.loads(mdata.group(1)) # list
        for sch in msg:      # sch is dict
            tmpdict = {}
            if sch.has_key('SCHEDULE_ID'):
                tmpdict['SCH_DATE'] = sch['SCH_DATE']
                tmpdict['SCHEDULE_ID'] = sch['SCHEDULE_ID']
                tmpdict['WEEK_DAY'] = sch['WEEK_DAY']
                SchId.append(tmpdict)
        if len(SchId) != 0:
            return { 'code':0, 'message':SchId }
        else:
            return { 'code':1, 'message':u'获取失败' }
    else:
        return { 'code':1, 'message':u'获取失败' }

def getDoctors(depid):
    doctors = {}
    for page in range(1,9):
        getDoctorsUrl = 'https://wxis.91160.com/wxis/doc/jsonList.do?depId=%s&p=%s' %(depid,page)
        try:
            response = requests.get(getDoctorsUrl,headers=headers,timeout=6)
        except:
            continue
        print response.text
        sys.exit()
        #response = json.loads(response.text,encoding='utf-8')
        if len(response) == 0:
            break
        else:
            for doc in response:
                doctors[str(doc['doctorId'])] = { 'doc_name':doc['doctorName'], 'doc_level':doc['zcid'] }
    return doctors
        

def getState(uid,depid,docid):
    getStateUrl = 'https://wxis.91160.com/wxis/doc/getState.do'
    data = { 'uid':uid, 'depid':depid, 'docid':docid }
    try:
        response = requests.post(getStateUrl,data=data,headers=headers,timeout=6).text
    except Exception,e:
        return { 'code':5 , 'message':u'请求超时' }
       
    state = int(json.loads(response)['data']['NUMBER_STATE'])
    if state == 1:
        return { 'code':1 , 'message':u'暂无排班' }
    elif state == 2:
        return { 'code':2 , 'message':u'可以预约' }
    elif state == 3:
        return { 'code':3 , 'message':u'已经约满' }
    else:
        return { 'code':4 , 'message':u'未知信息' }


def getOneDay(uid,depid,docid,schid,date):
    onedayList = []
    UrlAPI = 'https://wxis.91160.com/wxis/sch/getOneDay.do'
    data = { 
             'uid':uid,
             'depid':depid,
             'dep_name':department[depid],
             'docid':docid,
             'doc_name':doctors[docid]['doc_name'],
             'doc_level':doctors[docid]['doc_level'],
             'schid':schid,
             'querydate':date
           }

    try:
        response = requests.post(UrlAPI,data=data,headers=headers,timeout=5)
    except:
        return { 'code':1, 'message':u'请求超时' }
        
    OneDayData = json.loads(response.text)['data']['data']   # list
    if len(OneDayData) != 0:
        for onedaydata in OneDayData:
            tmpdict = {}
            if onedaydata['LEFT_NUM'] != 0:
                tmpdict['BEGIN_TIME'] = onedaydata['BEGIN_TIME']
                tmpdict['END_TIME'] = onedaydata['END_TIME']
                tmpdict['LEFT_NUM'] = str(onedaydata['LEFT_NUM'])
                tmpdict['TO_DATE'] = onedaydata['TO_DATE']
                onedayList.append(tmpdict)
        return {'code':0,'message':onedayList}
    else:
        return {'code':1, 'message':u'已经约满'}

def get_week_day(date):
    getdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    week_day_dict = { 0 : u'星期一', 1 : u'星期二', 2 : u'星期三', 3 : u'星期四', 4 : u'星期五', 5 : u'星期六', 6 : u'星期日' }
    return week_day_dict[getdate.weekday()]
        
        
            
def mail(msg):

    now = datetime.datetime.now()

    mail_host, mail_port = 'smtp.itdhz.com', 25
    mail_user, mail_pass = 'test@itdhz.com', 'qqww1122A'
    mail_recv = ['jaeson@itdhz.com']

    msg_text = msg
    content = MIMEText(msg_text, 'html', 'UTF-8')

    content['Subject'] = u'91160挂号预约'
    content['From'] = mail_user
    content['To'] = ';'.join(mail_recv)
    
    try:
        s = smtplib.SMTP(mail_host, mail_port)
        s.login(mail_user,mail_pass)
        s.sendmail(mail_user, mail_recv, content.as_string())
        s.close()
        print '%s 邮件发送成功!'%(now.strftime('%Y-%m-%d %H:%M:%S'))
    except smtplib.SMTPException:
        print '%s 邮件发送失败!'%(now.strftime('%Y-%m-%d %H:%M:%S'))




if __name__ == '__main__':
 
    uid = '8'
    hospital = { '8':'深圳市宝安区妇幼保健院' }

    depid = '200039207'
    department = { '200039207':'产科门诊(中心区新院)' }
    #depid = '200039163'
    #department = { '200039163':'妇科门诊(中心区新院)' }

    doctors = getDoctors(depid)
 
    sendmsg = ''

    print '>>>>>>>>>>>>>>>>' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '<<<<<<<<<<<<<<<<<<'

    ## docState
    for docid in doctors:
        doctorinfo = doctors[docid]['doc_name'] + '(' + doctors[docid]['doc_level'] + ')  '
        docstate = getState(uid,depid,docid)
        docstatecode = docstate['code']
        docstatemsg = docstate['message']
        #showmsg = doctorinfo + docstatemsg
        print doctorinfo,docstatemsg
        if docstatecode == 2:  # 1 暂无排班，2 可以预约，3 已经约满
            yyurl = 'https://wxis.91160.com/wxis/sch/main.do?unit_id=%s&dep_id=%s&doc_id=%s&dep_name=%s'%(uid,depid,docid,urllib.quote(department[depid]))
            yylink = '<a href='+yyurl+'>' + docstatemsg + '</a>'
            sendtmp = '<p>' + doctorinfo + yylink + '</p>'
            sendmsg = sendmsg + sendtmp
            ## docOneDay
            Result = getSchId(uid,depid,docid)
            if Result['code'] == 0:
                schidList = Result['message']  # list
                ## print + sendmsg
                for schid in schidList:     # schid is dict
                    ResultDetail = getOneDay(uid,depid,docid,schid['SCHEDULE_ID'],schid['SCH_DATE'])
                    if ResultDetail['code'] == 0:
                        OneDayDetail = ResultDetail['message']  # list
                        for oneday in OneDayDetail:
                            if oneday['LEFT_NUM'] != 0:
                                weekday = get_week_day(oneday['TO_DATE'])
                                print '  '+oneday['TO_DATE'],weekday,oneday['BEGIN_TIME']+'-'+oneday['END_TIME'],oneday['LEFT_NUM']
                                tmpone = '<p>'+oneday['TO_DATE']+' '+weekday+' '+oneday['BEGIN_TIME']+'-'+oneday['END_TIME']+' '+oneday['LEFT_NUM']+'</p>'
                                sendmsg = sendmsg + tmpone
    

    # send mail
    #if sendmsg != '':
    #    mail(sendmsg)

