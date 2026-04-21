#Author : AKSHAYA RAVI


from flask import Flask,render_template,request,Response,session
from pymongo import MongoClient
from PIL import Image
import matplotlib.pyplot as plt
import functions
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import gridfs

app = Flask(__name__)


@app.route('/')
@app.route('/home', methods=["GET", "POST"])
def home():
    return render_template('home.html')

'''@app.route('/about')
def about():
    return render_template('About.html')'''
       

@app.route('/scrapeData', methods=["GET", "POST"])
def scrapeData():
    url = request.form['weburl']
    valid=False
    records=[]
    client = MongoClient('localhost:27017')
    try:
        valid = functions.validate_url(url)
        links,valid_keys,rgb_imgs = functions.image_extractor(url)
        functions.insert_db(url,client,links,valid_keys)
        return render_template('home.html', length = len(links) ,links=links)
    except Exception as e:
     
        return render_template('home.html', message="Error recieved :" + str(e))
    
    
@app.route('/retrievbyName', methods=["GET", "POST"])
def retrievbyName():
    basename = request.form['baseurl']
    client = MongoClient('localhost:27017')
    try:
        links=functions.retrievefromdb(client,basename)
        return render_template('home.html', lengthOflinks = len(links) ,linksfromdb=links)
    except Exception as e:
        print(e)
        return render_template('home.html', retrievemessage="Error recieved :" + str(e))
    
@app.route('/updatekeywords', methods=["GET", "POST"])
def updatekeywords():
    basename = request.form['url']
    keywords = request.form['keywords']
    client = MongoClient('localhost:27017')
    updateMessage=functions.updatedb(client,basename,keywords)
    
    return render_template('home.html', updateMessage = updateMessage)
    

    
@app.route('/deletebyName', methods=["GET", "POST"])
def deletebyName():
    basename = request.form['deletebaseurl']
    client = MongoClient('localhost:27017')
    try:
        deleteMessage=functions.deletefromdb(client,basename)
        return render_template('home.html', deleteMessage=deleteMessage)
    except Exception as e:
        print(e)
        return render_template('home.html', deleteMessage="Error recieved :" + str(e)) 

@app.route('/savetolocal', methods=["GET", "POST"])
def savetolocal():
    images = functions.data.rgb_img
    for idx,i in enumerate(images):
        i.save("img"+str(idx)+".jpg")
    savedMessages = "Saved "+str(len(images))+" images."
    return render_template('home.html', savedMessages=savedMessages)


@app.route('/uploadfile', methods=["GET", "POST"])
def uploadfile():
    file = request.files['imgfile']
    keywords= request.form['imgkeywords']
    client = MongoClient('localhost:27017')
    uploadMessage=functions.uploadfiledb(client,file,keywords)
    
    return render_template('home.html', uploadMessage = uploadMessage)
        
    
@app.route('/retrieveimgfile', methods=["GET", "POST"])
def retrieveimgfile():
    keywords= request.form['imgkeywords']
    client = MongoClient('localhost:27017')
    image = functions.retrievefiledb(client,keywords)
    
    return render_template('home.html', image = image)
        
    
    

