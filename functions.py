#Author : AKSHAYA RAVI
# Msc in Artificial Intelligence Systems
import io
import urllib.request
import urllib.request as urllib2
from PIL import Image
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import gridfs
import codecs



class DataStore():
    rgb_img = []
   
    
data = DataStore()


def validate_url(url):
    try:
        f = urllib.request.urlopen(url)
        return  True
    except Exception as e:
        print(e)
        raise Exception(str(e) +
                      ' URL invalid. ')

def requesturl(links):
    valid=[]
    for i in links:
        v=False
        v = validate_url(i)
        valid.append(v)
        if v:
            f= urllib.request.urlopen(i)
            b = io.BytesIO(f.read())
            im = Image.open(b)
            im=im.convert('RGB')
            data.rgb_img.append(im)
    return data.rgb_img,valid
        
def image_extractor(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    tags=soup.find_all('img')
    links = list(tag['src'] for tag in tags if tag['src'].startswith('h') and tag['src'].endswith(('png','jpg','jpeg')))
    noOfimg=len(links)
    if noOfimg !=0:
        rgb_imgs,valid_keys = requesturl(links)
        return links,valid_keys,rgb_imgs
    else:
        raise Exception("Images may be protected/not found.No images could be retrieved")


def insert_db(baseurl,client,links,valid_keys):
    db = client['webscraper']   
    collection = db['url']
    records=[]
    for idx,i in enumerate(links):
        record={}
        #record['id']=collection.find().Count()+1
        base_url_parse=urlparse(baseurl)
        record['website_url'] = base_url_parse.netloc
        record['id_name']=base_url_parse.netloc.split('.')[1]
        record['completeurl'] = baseurl
        record['keysfromsub'] = ','.join(filter(None, base_url_parse.path.split('/')))
        record['imageurl']= i
        record['valid']= valid_keys[idx]
        records.append(record)
    x = collection.insert_many(records)
    return "Added successfully"

def retrievefromdb(client,basename):
    db = client['webscraper']   
    collection = db['url']
    links=[]
    for x in collection.find({ "id_name": basename, "valid": True }).limit(15):
        links.append(x["imageurl"])
    if len(links)==0:
         raise Exception("No images found for base url")
    else:
        return links
        
def updatedb(client,basename,keywords):
    db = client['webscraper']   
    collection = db['url']
    query = { "id_name": basename }
    newvalues = { "$set": { "keysfromsub": keywords } }

    update_records = collection.update_many(query, newvalues)

    return str(update_records.matched_count)+ " documents updated."

    
def deletefromdb(client,basename) :
    db = client['webscraper']   
    collection = db['url']
    result = collection.delete_many({"id_name": basename})
    
    return str( result.deleted_count)+ " documents deleted."
   
    
def uploadfiledb(client,file,keywords):
    db = client['webscraper']   
    collection = db['userimages']
    fs = gridfs.GridFS(db)
    fs.put(file , keywords =keywords , filename = file.filename )
    collection.insert_one({'keywords':keywords , 'filename' : file.filename})
    return "Uplaoded file"

def retrievefiledb(client,keywords):
    db = client['webscraper']   
    collection = db['userimages']
    fs = gridfs.GridFS(db)
    item = collection.find_one({'keywords': keywords})
    image = fs.find_one({"filename": item['filename']})
    base64_data = codecs.encode(image.read(), 'base64')
    image = base64_data.decode('utf-8')
    
    return image
    

