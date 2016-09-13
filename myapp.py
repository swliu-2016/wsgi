#!/usr/bin/python

# Coded by Siwei Liu
# Date 2016-09-13
# Version 1.0.4

import os
import sys
import time
import psycopg2
import subprocess
import zlib

######################################################
# Screenfetch
def getscreenfetch():
    p = subprocess.Popen('screenfetch', stdout=subprocess.PIPE)
    out, err = p.communicate()
    tmp = out.decode('unicode-escape')
    tmp = tmp.replace('[0m', '')
    tmp = tmp.replace('[1;36m','')
    tmp = tmp.replace('[36m','')
    tmp = tmp.replace('[1m', '') #@[0m[0m[1;36mserver[0m
    return(tmp)

######################################################
# Get CPU information
def read_cpu_info():
    try:
        numbercpu = 0
        fd = open("/proc/cpuinfo", "r")
        for line in open("/proc/cpuinfo", "r"):
            line = fd.readline()
            if line.find('processor') >= 0:
                numbercpu += 1
            if line.find('model name') >= 0:
                cputech = ' '.join(line.split()[3:len(line.split())])
            if line.find('Features') >= 0:
                cpufeatures = ' '.join(line.split()[2:len(line.split())])
    finally:
        if fd:
            fd.close()
        else:
            return("Error on open /proc/cpuinfo file!")
    return([numbercpu, cputech, cpufeatures])

######################################################
# Get OS Version Information
def read_os_version():
    try:
        fd = open("/proc/version", 'r')
        for line in open("/proc/version", 'r'):
            line = fd.readline()
            osver = ' '.join(line.split()[0:3])
            gccver = ' '.join(line.split()[4:7])
    finally:
        if fd:
            fd.close()
        else:
            return("Error on open /proc/version file!")
    return([osver, gccver])

######################################################
# Get CPU temperature
def read_cpu_temp():
    try:
        fd = open("/sys/class/thermal/thermal_zone0/temp", 'r')
        cpu_temp = fd.read()
    finally:
        if fd:
            fd.close()
        else:
            return("Error on open /sys/class/thermal/thermal_zone0/temp file!")
    cpu_temp_str = "%.2f &#x2103;" % (float(cpu_temp)/1000)
    return(cpu_temp_str)

######################################################
"""
# Get GPU temperature
def read_gpu_temp():
    #gpu_temp = subprocess.call("vcgencmd measure_temp").replace('temp=', '').replace('\'C', '')
    p = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)

    gputempstr = b''.join(p.stdout.readlines()).decode()
    gputemp = ".".join(re.findall(r'(\w*[0-9]+)\w*.', gputempstr))

    return(gputemp + " &#x2103;")
"""
######################################################
# Define HTML style
def html_pre_css():
    mystyle =  """
        <style type="text/css">
        pre{
            white-space:pre-wrap;/*css-3*/
            white-space:-moz-pre-wrap;/*Mozilla,since1999*/
            white-space:-pre-wrap;/*Opera4-6*/
            white-space:-o-pre-wrap;/*Opera7*/
            word-wrap:break-word;/*InternetExplorer5.5+*/　　
        } 
        </style>
        """
    return(mystyle)

######################################################
# Database connect
def db_connect(dbstr):
    dbhandler = {}
    conn = psycopg2.connect(dbstr)
    cursor = conn.cursor()
    dbhandler['conn'] = conn
    dbhandler['cursor'] = cursor
    return(dbhandler)

######################################################
# Database close
def db_close(db):
    db['cursor'].close()
    db['conn'].close()

######################################################
# Database get the last 10 records
def visitor_db_query():
    # databae operate
    db = db_connect("dbname=webstat user=postgres password=lswgyt")       # db is a list

    db['cursor'].execute("SELECT count(*) from webstat")
    rows = db['cursor'].fetchall()
    for row in rows:
        totalrecs = row[0]

    htmlstrList = []
    htmlstrList.append(html_pre_css())

    htmlstrList.append("<pre>")
    db['cursor'].execute("select * from webstat order by id desc limit 10")
    rows = db['cursor'].fetchall()
    for row in rows:
        htmlstrList.append("<font style='color:#FF0000'>>>>>>>>>>></font><br>")
        htmlstrList.append("Record:           <font style='color:#FF0000;font-weight:bold'>%s</font><br>" % row[0])
        htmlstrList.append("<font style='color:#0000FF'>Client IP Addr:</font>   %s <br>"                 % row[1])
        htmlstrList.append("<font style='color:#00D200'>User Agent:</font>       %s <br>"                 % row[2])
        htmlstrList.append("<font style='color:#0000FF'>Record Time:</font>      %s <br>"                 % row[3])
        htmlstrList.append("<font style='color:#00D200'>Request URI:</font>      %s <br>"                 % row[4])
        htmlstrList.append("<font style='color:#0000FF'>Server Soft:</font>      %s <br>"                 % row[5])
        htmlstrList.append("<font style='color:#00D200'>Server IP Addr:</font>   %s <br>"                 % row[6])
        htmlstrList.append("<font style='color:#0000FF'>CPU Temperature:</font>  %s <br>"                 % row[7])
        htmlstrList.append("<font style='color:#00D200'>Server Info:</font>      %s <br>"                 % row[8])
        htmlstrList.append("<br>")

    htmlstrList.append("<br>")
    htmlstrList.append("Total record(s): %s" % totalrecs)

    db_close(db)

    return(''.join(htmlstrList))

######################################################
# Database write
def db_write(webrequest):
    ipaddr       = webrequest["REMOTE_ADDR"]
    useragent    = webrequest["HTTP_USER_AGENT"]
    curtime      = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
    requesturi   = webrequest["REQUEST_URI"]
    serversoft   = webrequest["SERVER_SOFTWARE"]
    serverip     = getserverip()
    servertemp   = read_cpu_temp()
    serverinfo   = getscreenfetch()

    # databae operate
    db = db_connect("dbname=webstat user=postgres password=lswgyt")

    sqlstr = "insert into webstat(ipaddr, useragent, visitingtime, requesturi, serversoft, serverip, servertemp, serverinfo) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(ipaddr, useragent, curtime, requesturi, serversoft, serverip, servertemp, serverinfo)
    db['cursor'].execute(sqlstr)
    db['conn'].commit()

    db_close(db)

######################################################
# Get OS state
def getserverip():
    #p = subprocess.Popen(['curl', '-s', 'ident.me'], stdout=subprocess.PIPE)
    p = subprocess.Popen(['curl', '-s', 'ip.cip.cc'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    serverip = out.decode()

    return(serverip)

######################################################
# Get Server Information
def serverinfo():
    htmlstrList = []
    htmlstrList.append(html_pre_css())

    # Font color change along with time:
    t = time.localtime(time.time())
    cA  = int(int(time.strftime("%H", t))*11.08695652)
    cB  = int(int(time.strftime("%M", t))*4.3220338983)
    cC  = int(int(time.strftime("%S", t))*4.3220338983)
    ct = '%02.X%02.X%02.X' % (cA, cB, cC)
    ct = ct.replace('0x', '')
    """
    cA = random.randint(0, 255)
    cB = random.randint(0, 255)
    cC = random.randint(0, 255)
    ct = '%02.X%02.X%02.X' % (cA, cB, cC)  # keep two number in HEX format
    ct = ct.replace('0x', '')
    """

    htmlstrList.append("<h2>Server Running Information</h2>")
    htmlstrList.append("<pre><font style='color:#%s'>" % ct)
    htmlstrList.append(getscreenfetch())
    htmlstrList.append("</font></pre>")

    htmlstrList.append("<p>Color code: <font style='color:#%s'>#%s</font></p>" % (ct.upper(), ct.upper()))

    htmlstrList.append("CPU Temperature: <font style='color:#FF0000'>%s</font>" % read_cpu_temp())
    htmlstrList.append("&nbsp;&nbsp;&nbsp;&nbsp;Server IP: <font style='color:#FF0000'>%s</font>" % getserverip())

    htmlstrList.append("<br>")

    time_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
    htmlstrList.append("Current Server Time: <font style='color:#0000FF'>%s</font>" % time_str)

    return(''.join(htmlstrList))

######################################################
# The First Web Page
def index(_header):
    db_write(_header)
    htmlstrList = []
    htmlstrList.append("""
        <HTML>
        <HEAD>
        <TITLE>Personal website written by Flask & PostgreSQL</TITLE>
        </HEAD>
        <style type='text/css'>
        a:hover{color:red; font-weight:bold;text-decoration:none;}  
        a:link{color:blue;text-decoration:none;} 
        a:visited{color:blue;text-decoration:underline;} 
        body{
           color:#FF0000
           font-size:10px;
        }
        #bNav{
           font-size:20px;
           margin-top:10px;
           background:#D9EBF5;
           text-align:center;
           width:100%
        }
        #bNav ul{
           padding:4px 0;
           margin:0;
           overflow:hidden;
        }
        #bNav ul li{
        display:inline;
        margin-left:9px;
        padding:0;
        }
    </style>
    <BODY>
    <div id='bNav' class='bNav'>
    <ul>
    <li><a href='/webui-aria2'   target='_blank'>WebUI</a></li>
    <li>|</li>
    <li><a href='memo'     target='_blank'>Memo</a></li>
    <li>|</li>
    <li><a href='photos'   target='_blank'>Photo Gallery</a></li>
    <li>|</li>
    <li><a href='visitors' target='_blank'>Visitors</a></li>
    <li>|</li>
    <li><a href='memodb'   target='_blank'>Memo DB</a></li>
    <li>|</li>
    <li><a href='/doc'     target='_blank'>Documents</a></li>
    </ul>
    </div>
    </BODY>
    </HTML>
    """)
    htmlstrList.append(serverinfo())
    htmlstrList.append("<br>")
    htmlstrList.append("<br>")
    htmlstrList.append("<p align='center'>")
    htmlstrList.append("<img src='/logo/python-logo.png' width=200 height=60 />")
    htmlstrList.append("  <img src='/logo/hdr_left.png' width=200 height=60 />")
    htmlstrList.append("  <img src='/logo/asf_logo.png' width=200 height=60 />")
    htmlstrList.append("</p>")

    return(''.join(htmlstrList))

######################################################
# Get Web Request and Headers
def get_headers(request):
    db_write(request.environ)
    headers = []
    headers.append("<br><br><h2>HTTP Request Environ:</h2>")
    for (k,v) in request.environ.items():
        headers.append("<LI><span style='color:green'>%s</span>:%s</LI>"%(k, str(v)))
    headers += "<br><br><h2>HTTP Request Headers:</h2>"
    for (k,v) in request.headers.items():
        headers.append("<LI><span style='color:green'>%s</span>:%s</LI>"%(k, str(v)))

    return(''.join(headers))

#######################################################
# Web Page Define
def memoindex(_header):
    db_write(_header)
    htmlstr = """
        <style>
        textarea
        {
        width:95%;
        height:80%;
        }
        </style>
        <form action='writememo' method=post>
        <dl>
            <dd><font style='color:#0000FF;font-weight:bold'>Title:</font>
            <dd><input type=text name=title style="width:95%;overflow-x:visible;overflow-y:visible;">
            <dd><font style='color:#0000FF;font-weight:bold'>Text Content:</font>
            <dd><textarea name=text></textarea>
            <br>
            <dd><input type=submit value='Send text to server!'>
        </dl>
        </form>
    """
    return(htmlstr)

#######################################################
# Database max pages
def memodb_max_pages():
    totalrecs = 0
    pages = 0

    db = db_connect("dbname=webstat user=postgres password=lswgyt")
    db['cursor'].execute("SELECT count(*) from memo")

    rows = db['cursor'].fetchall()
    for row in rows:
        totalrecs = row[0]
    db_close(db)

    recs_in_one_page = 30

    if totalrecs % recs_in_one_page == 0:
        pages = int(totalrecs / recs_in_one_page)
    else:
        pages = int(totalrecs / recs_in_one_page) + 1

    return(pages)

#######################################################
# Database query and display
def memodb_read(_header):
    db_write(_header)
    db_page_size = memodb_max_pages()

    htmlstr = "<h2>Memo Database List in Page(s)</h2><br>"
    for pageIndex in range(memodb_max_pages()):
        htmlstr += "<a href='memopage?id=%s' target='_blank'>Pages %s</a> &nbsp;&nbsp;" % (pageIndex, pageIndex+1)
    return(htmlstr)

#######################################################
def memodb_read_page(id, _header):
    db_write(_header)

    htmlstrList = []
    recs_in_one_page = 30
    page_id = int(id)

    db = db_connect("dbname=webstat user=postgres password=lswgyt")
    sqlstr = "SELECT * from memo where id between %d and %d order by id desc" % (recs_in_one_page*(memodb_max_pages()-page_id-1)+1, recs_in_one_page*(memodb_max_pages()-page_id))
    db['cursor'].execute(sqlstr)
    rows = db['cursor'].fetchall()
    for row in rows:
        title = zlib.decompress(row[1]).decode()
        htmlstrList.append("<li><a href='memoid?id=%s' target='_blank'>%s</a></li><br>" % (row[0], title))

    db_close(db)
    return(''.join(htmlstrList))

#######################################################
# Database read by ID
def memodb_byID(id, _header):
    db_write(_header)

    htmlstrList = []
    htmlstrList.append(html_pre_css())
    htmlstrList.append("<pre>")

    db = db_connect("dbname=webstat user=postgres password=lswgyt")
    sqlstr = "SELECT * from memo where id=%s" % id
    db['cursor'].execute(sqlstr)
    rows = db['cursor'].fetchall()
    for row in rows:
        title = zlib.decompress(row[1]).decode()
        text  = zlib.decompress(row[2]).decode()
        text  = text.replace("<", '&lt;')
        text  = text.replace(">", '&gt;')
        insdate = zlib.decompress(row[3]).decode()

        htmlstrList.append("<title>%s</title>" % title)
        htmlstrList.append("<h2><font style='color:#FF0000'>%s</font></h2><br><div style='color:blue'>%s</div><br>%s" % (title, insdate, text))
    htmlstrList.append("</pre>")

    db_close(db)

    return(''.join(htmlstrList))

#######################################################
# Database write
def memodb_write(data, _header):
    db_write(_header)

    title   = zlib.compress(data[0].encode())
    text    = zlib.compress(data[1].encode())
    timein  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    insdate = zlib.compress(timein.encode())

    # databae operate
    db = db_connect("dbname=webstat user=postgres password=lswgyt")
    db['cursor'].execute("insert into memo(title, text, insdate) values (%s, %s, %s);", (psycopg2.Binary(title), psycopg2.Binary(text), psycopg2.Binary(insdate)))
    db['conn'].commit()

    db_close(db)

    return("Data has been uploaded. Thank you!")

#############################################################
# Get Photos names and put them into a List
def imgInfo(imgPath):
    fileList = []
    fileNum = 0

    files = os.listdir(imgPath)

    for f in files:
        filePath = imgPath + os.sep + f
        if(os.path.isfile(filePath)):
            fileNum = fileNum + 1
            fileList.append(f)
        elif(os.path.isdir(filePath)):
            imgInfo(filePath)

    fileList.sort()
    return(fileNum, fileList)

#############################################################
# Display the photos
def imgdisplay(imgpath, _header):
    db_write(_header)

    NIPL = 6 # How many photos per line.
    htmlstrList = []
    htmlstrList.append("<H1 align=center>%s</H1>\n" % imgpath)
    photoPath = "/srv/http/photos/%s/thumb" % imgpath 
    thumbPhotoPath = photoPath.replace("/srv/http", "")
    bigPhotoPath = thumbPhotoPath.replace("/thumb", "")

    imgs = imgInfo(photoPath)
    if(imgs[0]/NIPL - int(imgs[0]/NIPL) > 0):
        numaline = int(imgs[0]/NIPL)+1
    else:
        numaline = int(imgs[0]/NIPL)
    numofimgs = len(imgs[1])

    for i in range(numaline):
        htmlstrList.append("<p align=center>\n")
        for j in range(NIPL):
            pos = i * NIPL + j
            if(pos >= numofimgs):
                for voidimg in range(NIPL*numaline-numofimgs):
                    htmlstrList.append(" <img src='' width=150 height=150 />")
                break
            htmlstrList.append(" <a href='%s/%s' target='_blank'><img src='%s/%s'></a>\n" % (bigPhotoPath, imgs[1][pos], thumbPhotoPath, imgs[1][pos]))
        htmlstrList.append("</p>")
    return(''.join(htmlstrList))

###########################################################
# Rearrange photos path and name into a sorted List
def dirInfo(imgPath):
    dirList = [] # Due to dirList wipe off in every loop, so, the second or more deep dir will be skip

    files = os.listdir(imgPath)

    for f in files:
        filePath = imgPath + os.sep + f
        if(os.path.isdir(filePath)):
            dirList.append(f)
            dirInfo(filePath)

    dirList.sort()
    return(dirList)

#############################################################
# HTML format
def html_dir_output(year, dirs):
    NIPL = 6 # How many photos per line.
    htmlstrList = []

    htmlstrList.append("<H2>%s</H2>"%year)
    numofdirs = len(dirs)

    if(numofdirs/NIPL - int(numofdirs/NIPL) > 0):
        numaline = int(numofdirs/NIPL)+1
    else:
        numaline = int(numofdirs/NIPL)

    for i in range(numaline):
        htmlstrList.append("<P>")
        for j in range(NIPL):
            pos = i * NIPL + j
            if(pos >= numofdirs):
                for voidimg in range(NIPL*numaline-numofdirs):
                    pass
                break

            htmlstrList.append(" <a href='/wsgi/imgdisplay?dir=%s' target='_blank'>%s</a>\n" % (dirs[pos], dirs[pos]))
        htmlstrList.append("</P>")
    return(''.join(htmlstrList))


#############################################################
# List the dirs
def listdir(_header):
    db_write(_header)

    photoPath = "/srv/http/photos" # Photo path, you can change it according server config!
    htmlstrList = []
    htmlstrList.append("<H1 align=center>Photograph Gallery</H1>")
    Alldirs = dirInfo(photoPath)
    year = ''
    yearItemList = []
    year_dirs = []

    for item in Alldirs:
        if(year == item[0:4]):
            yearItemList.append((year, item))
        else:
            year = item[0:4]
            yearItemList.append((year, item))

    year = ''
    for item in yearItemList:
        if(item[0] == '.syn'):
            continue
        elif(year == item[0]):
            year_dirs.append(item[1])
        else:
            if(item[0]=='Othe'):
                htmlstrList.append(html_dir_output(year, year_dirs))
                htmlstrList.append(html_dir_output('Other Photos', [item[1]]))
                break
            htmlstrList.append(html_dir_output(year, year_dirs))
            year_dirs.clear()
            year = item[0]
            year_dirs.append(item[1])
    return(''.join(htmlstrList))

