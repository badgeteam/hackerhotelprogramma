import urllib3
import html5lib
import json
import hashlib
import datetime

eventtitle='Hacker Hotel'
version='HAAT AAN WORDPRESS'
days= { 15: '2019-02-15',
        16: '2019-02-16',
        17: '2019-02-17'}


def traversetag(todo,lookfor,found,debug=False):
  if todo.tag==lookfor: found.append(todo)
  for x in todo:
    if(debug): print(x.tag,x.attrib)
    if x.tag==lookfor:
        found.append(x)
    found=traverse(x,lookfor,found,debug)
  return found 
def traverse(todo,lookfor,found,debug=False):
  for x in todo:
    if(debug): print(x.tag,x.attrib)
    if 'class' in x.attrib and x.attrib['class']==lookfor:
        found.append(x)
    found=traverse(x,lookfor,found,debug)
  return found 

def getthetext(todo):
    text=None
    for x in todo:
      if x.tag=='{http://www.w3.org/1999/xhtml}p' and text==None:
        text=x.text
      if text==None:
        divs=traversetag(x,'{http://www.w3.org/1999/xhtml}div',[])
        for div in divs:
          if text==None: text=div.text
          if text!=None and text.rstrip()=="": text=None
          if 'aria-label' in div.attrib and text==None: text=div.attrib['aria-label']
          if text!=None and text.rstrip()=="": text=None
          if text==None:
            for test in div:
              if text==None: text=test.text
              if text!=None and text.rstrip()=="": text=None
    return(text)
def getabstract(url):
  doc=fetchurl(url)
  parent_map = {c:p for p in doc.iter() for c in p}
  try:
    text=None
    todo=traverse(doc,'entry-content',[])
    text=getthetext(todo[0])
    if text==None:
      text=getthetext(todo)
    if text!=None: return(text)
    return(" ")
  except IndexError:
    return(" ")
  return(" ")
   

def eventstoev(day,events,evtype):
  FMT = '%Y-%m-%d %H:%M:%S'
  global days
  rev=[]
  for event in events:
    if len(event):
      newev={}
      newev['room']=event.attrib['data-column-id']
      newev['eventid']=event[0].attrib['data-event-id']
      newev['title']=event[0][0][0].attrib['title']
      newev['url']=event[0][0][0].attrib['href']
      newev['start']=event[0][0][1][0].attrib['datetime']
      newev['end']=event[0][0][1][2].attrib['datetime']
      speaker=traverse(event,'event-subtitle',[])
      newev['speaker']='Henk de Vries'
      newev['guid']="1fbad090-4bcb-42ef-%04d-971e8e549f64" % int( newev['eventid'] )
      if(len(speaker)): newev['speaker']=speaker[0].text
      if newev!={}:
        newev['day']=int(day.split(" ")[1].replace('th',''))
        newev['realdatetimestart']=days[newev['day']]+' '+newev['start']+':00'
        newev['realdatetimeend']=(days[newev['day']+1] if newev['end'].startswith('0') else  days[newev['day']])+' '+newev['end']+':00'
        newev['timestamp']=int(datetime.datetime.strptime(newev['realdatetimestart'], '%Y-%m-%d %H:%M:%S').strftime("%s"))
        newev['duration'] = "{:0>8}".format(str(datetime.datetime.strptime(newev['realdatetimeend'], FMT) - datetime.datetime.strptime(newev['realdatetimestart'], FMT)))[0:5]
        newev['subtitle']=""
        newev['language']=""
        newev['abstract']=getabstract(newev['url'])
        newev['description']=newev['abstract']
        newev['when']=newev['start']
        newev['type']=evtype
        newev['recording_license']=""
        newev['do_not_record']=False
        newev['persons']=[x for x in newev['speaker'].replace(" & ",", ").split(", ")]
        rev+=[newev]
  return(rev)



roomnums={}
def fetchurl(url):
  m = hashlib.md5()
  m.update(url.encode('utf-8'))
  filename="cache/"+m.hexdigest()
  try:
      html=open(filename,"r").read()
  except:
      http = urllib3.PoolManager()
      html= http.request('GET',url=url).data
      open(filename,"wb").write(html)
  doc = html5lib.parse(html)
  return doc

def getevents(url,eventtype):
  global roomnums
  doc=fetchurl(url)
  realev=[]
  parent_map = {c:p for p in doc.iter() for c in p}
  start=traverse(doc,'entry-content',[])[0]
  for x in start:
    if x.tag=='{http://www.w3.org/1999/xhtml}h1':
      day=x.text
    if x.tag=='{http://www.w3.org/1999/xhtml}div':
      for tab in x:
        scodes=traverse(tab,'mptt-shortcode-row',[])
        for scode in scodes:
          for row in scode:
            roomnums[row.attrib['data-column-id']]=row.text
        events=traverse(tab,'mptt-shortcode-event  mptt-event-vertical-default',[])
        e1=eventstoev(day,events,eventtype)
        events=traverse(tab,'mptt-shortcode-event mptt-grouped-event mptt-event-vertical-default',[])
        e2=eventstoev(day,events,eventtype)
        if len(e1): realev+=e1
        if len(e2): realev+=e2
  return realev
allev=[]
allev+=getevents('https://hackerhotel.nl/index.php/lectures-schedule/','lecture')
allev+=getevents('https://hackerhotel.nl/index.php/workshops-schedule/','workshop')

# Because Wordpress is fucking unbelieveable stupid sometimes we get everything double
cd={}
for ev in allev:
  evid=ev['eventid']
  cd[evid]=ev

realdays=[x for x in days]
realdays={str(x):days[realdays[x]] for x in range(0,len(realdays))}
obj={"version": version, "title": eventtitle, "days": realdays}
with open("schedule/schedule.json","w") as f:
   f.write(json.dumps(obj))
   f.close()

i=0
for dagnummer in days:
    rooms={}
    roomstoday={}
    for eventid in cd:
      if cd[eventid]['day']==dagnummer:
          roomstoday[cd[eventid]['room']]=roomnums[cd[eventid]['room']]
    for roomnum in roomstoday:
        roomname=roomstoday[roomnum]
        rooms[roomname]=[]
        for eventid in cd:
            if cd[eventid]['day']==dagnummer and cd[eventid]['room']==roomnum:
                newobj={}
                for x in ['start','duration','title','guid']:
                  newobj[x]=cd[eventid][x]
                rooms[roomname].append(newobj)
    
    obj={"version": version, "date": days[dagnummer], "rooms": rooms}
    with open("schedule/day/%d.json" % i,"w") as f:
       f.write(json.dumps(obj))
       f.close()
    i+=1


for eventid in cd:
  newobj={}
  for x in ['timestamp','duration','room','title','subtitle','type','language','abstract','description','recording_license','do_not_record','guid','when','persons']:
    newobj[x]=cd[eventid][x]
  guid=cd[eventid]['guid']
  open("schedule/event/"+guid,"w").write(json.dumps(newobj))
    
  
