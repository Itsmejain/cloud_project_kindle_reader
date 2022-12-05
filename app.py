from flask import Flask,render_template,request,redirect,url_for
import time

# import mysql
import mysql.connector
import os
from datetime import datetime
import base64
from werkzeug.utils import secure_filename

import boto3
from config import S3_BUCKET,S3_KEY,S3_SECRET
import creds as cred 
UPLOAD_FOLDER = 'uploads'
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )


app = Flask(__name__,template_folder="./templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# s31 = boto3.client(
#         's3'
#         # aws_access_key_id="AKIAXM6N3EKOEYRBUJFO",
#         # aws_secret_access_key="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"
#     )
def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(
            file,
            os.getenv("AWS_BUCKET_NAME"),
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename

@app.route("/")
@app.route("/admin")
def adminfunction():
    
    return render_template("adminportal.html")

@app.route("/addbook",methods=['GET','POST'])
def addbookfunctionality():
    bookname = request.form['bookname']
    bookdescription = request.form['bookdesc']
    bookcoverimg = request.files['bookcover']
    bookpdf = request.files['bookpdf']

    # now = datetime.now.getMil()
    current_time = round(time.time() * 1000)
    # current_time = now.strftime("%H:%M:%S")
    
    bookid = str(current_time)+"_"+bookname.replace(" ","_")
    print(bookid,bookdescription)



    bookcoverimg.save(os.path.join(app.config['UPLOAD_FOLDER'],bookid+".jpg"))

    bookpdf.save(os.path.join(app.config['UPLOAD_FOLDER'],bookid+".pdf"))

    
    #
    dataBase = mysql.connector.connect(
    host ="localhost",
    user ="root",
    passwd ="",
    database = "bookdb"
    )
    # print(dataBase)
    cursorObject = dataBase.cursor()
    bookcoverimagepath = 'uploads/'+str(bookid)+".jpg"
    bookpdfpath = 'uploads/'+str(bookid)+".pdf"
    img_file_blob = convertToBinaryData(bookcoverimagepath)
    sql_insert_blob_query = """ INSERT INTO books
                           (book_id, book_name, book_image,
                           book_description) VALUES (%s,%s,%s,%s)"""

    val = (bookid,bookname,img_file_blob,bookdescription)
    cursorObject.execute(sql_insert_blob_query,val)
    dataBase.commit()
    dataBase.close()

    #book has been added

    #save pdf to s3 
    output = "----"

    output = s3.upload_file(bookpdfpath, cred.S3_BUCKET,bookid+'.pdf', ExtraArgs=None, Callback=None, Config=None)

    print(output)
    # with open(bookpdfpath, 'rb') as data:
        # output = upload_file_to_s3(data)
        # s3.upload_fileobj(data, , 'mykey')
    #  upload_file_to_s3(bookpdf)
        
        # if upload success,will return file name of uploaded file
    # if output:
    #     print("Success upload")
    #         # write your code here 
    #         # to save the file name in database

    #         # 
    #     return "<p>Success upload</p>"

    #     # upload failed, redirect to upload page
    # else:
    #     print("Failure upload")
            # write your code here 
            # to save the file name in database

            # 
        # return "<p>FAILURE upload</p>"

    
    return render_template("adminportal.html")



@app.route("/asdsa")
def s3test():
    print(cred.S3_SECRET)
    print(cred.S3_BUCKET)
    print(cred.S3_KEY)


    

    
    output = upload_file_to_s3('banner.jpg')
        
        # if upload success,will return file name of uploaded file
    if output:
        print("Success upload")
            # write your code here 
            # to save the file name in database

            # 
        return "<p>Success upload</p>"

        # upload failed, redirect to upload page
    else:
        print("Failure upload")
            # write your code here 
            # to save the file name in database

            # 
        return "<p>FAILURE upload</p>"
            
    # s3_resouce = boto3.resource('s3')
    # # boto3.set_stream_logger('botocore', level='DEBUG')
    # my_bucket = s3_resouce.Bucket('cloudcomputingiiitd')
    # for my_bucket_object in my_bucket.objects.all():
    #     print(my_bucket_object)
    
    # summaries = my_bucket.objects.all()
    # print(my_bucket.creation_date)
    return render_template('files.html')



    return "<p>hello world</p>"

def convertToBinaryData(filename):
# Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


#route home api
# @app.route("/")
@app.route("/index.html")
def home():
 return render_template('index.html')

@app.route("/register.html")
def register():
 return render_template('register.html')


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/allbooks",methods=['GET','POST'])
def allbooks():

    dataBase = mysql.connector.connect(
    host ="localhost",
    user ="root",
    passwd ="",
    database = "bookdb"
    )
    print(dataBase)
    cursorObject = dataBase.cursor()

    # insertquery = 
    # img_file = convertToBinaryData("testimage.jpg")
    # sql_insert_blob_query = """ INSERT INTO books
    #                        (id, name, image) VALUES (%s,%s,%s)"""

    # val = [("bid2","boook name 2", img_file),("bid3","boook name 3", img_file)
    # ,("bid4","boook name 4", img_file),("bid5","boook name 5", img_file)]
    # # # insert_blob_tuple = 
    # # # r = cursorObject.execute(sql_insert_blob_query, insert_blob_tuple)
    # cursorObject.executemany(sql_insert_blob_query, val)
    # dataBase.commit()



    query = "SELECT * from books"
    cursorObject.execute(query)
    myresult = cursorObject.fetchall()
    
    booksdata = []
     
    for bookitem  in myresult:
        tempdict = {}
        tempdict['book_title'] = bookitem[1]
        tempdict['book_description'] = bookitem[3]
        blobimagedata =  base64.b64encode(bookitem[2])
        blobimagedata =blobimagedata.decode("UTF-8")
        tempdict['book_img'] = blobimagedata
        booksdata.append(tempdict)
    dataBase.close()
    print(type(booksdata))
    print(booksdata)



    booksdata1 = [
        {"book_title": "book1","book_description": "book1 description ","book_img": "https://images.indianexpress.com/2022/12/Umar-Khalid.jpg"},
         {"book_title": "book2","book_description": "book2 description ","book_img": "https://c.ndtvimg.com/2022-12/g7nlvg58_3-killed-in-bomb-blast-at-trinamool-leaders-house_625x300_03_December_22.jpg"}
         ]
    return render_template("allbookspage.html",booksdata = booksdata)



@app.route("/mybooks",methods=['GET','POST'])
def mybooks():
    return render_template("mybookspage.html")

if __name__ == "__main__":
 app.run(debug=True,port=5000)
