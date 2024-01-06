# import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as  uReq 
import logging 
from flask_cors import CORS,cross_origin
from flask import Flask ,render_template,request,jsonify
import pymongo

mongo_client=pymongo.MongoClient("mongodb+srv://saksham:qk70nd97a@cluster1.vucvhcs.mongodb.net/?retryWrites=true&w=majority")
db=mongo_client["datascience"]
collection=db["Web_Scrapper_Rcords"]

logging.basicConfig(filename='web_scrapeer.log',level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')

app=Flask(__name__)

@app.route("/",methods=["GET"])
@cross_origin()
def home_page():
    return render_template("index.html")

@app.route("/review",methods=["POST","GET"])
@cross_origin()
def index():
    if request.method =="POST":
        try:
            searchString=(request.form["content"]).replace(" ","")
            flipcart_url="https://www.flipkart.com/search?q="+searchString
            uClient=uReq(flipcart_url)
            flipcart_page=uClient.read()
            uClient.close()
            flipcart_html=bs(flipcart_page,"html.parser")
            bigbox=flipcart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
            del bigbox[:3]
            # del bigbox[-5:]
            box = bigbox[0]
            productLink= "https://www.flipkart.com"+box.div.div.div.a['href']
            product=uReq(productLink)
            x=product.read()
            product.close()
            pro_html=bs(x,"html.parser")
            # print(pro_html)
            
            comentbox=pro_html.find_all("div",{"class":"_16PBlm"})

            # filename=searchString+".csv"
            # fw=open(filename,"w")
            # headers="Product, Name, Rating, CommentHead, Comment \n"            
            # fw.write(headers)
            
            reviews=[]
            # Names  
            for i in comentbox:
                try:
                    name=i.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text                  
                except:
                    logging.info("name")
            # Ratings    
                try:
                    rating=(i.div.div.div.div.text)
                except:
                    rating="Sorry NO Ratings for this Product \U0001F647"
                    logging.info("Ratings")
                
                #comments heading
                try:                    
                    commentHead=(i.div.div.div.p.text)
                except:
                    commentHead="NO comment Heading"   
                    logging.info("cmmentHeading")
                    
                try:
                    comtag=(i.div.div.find_all("div",{"class":""})) 
                    custComment=comtag[0].div.text
                
                except Exception as e :
                    logging.error(e)
                    
                    
                mydict={"Product":searchString+"_Fourth_result","Name":name,"Rating":rating,"CommentHead":commentHead,"Comment":custComment}
                reviews.append(mydict)
            collection.insert_many(reviews)
            logging.info("My finall Result is Saved in MongoDB ") 
            # fw.close()
            return render_template("result.html",reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.error(e)
            return "Something went wrong \U0001F629"


if __name__=="__main__":
    app.run(host="0.0.0.0")


























