from flask import Flask,render_template,request,redirect,url_for,send_file,session
import time
import mysql.connector
import os
from flask import *  
import base64
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
# from config import S3_BUCKET,S3_KEY,S3_SECRET
import creds as cred
from cryptography.fernet import Fernet
import webbrowser
from flask_session.__init__ import Session
# from flask.ext.session import Session
    
# import Session


key = bytes.fromhex("47513459507931446361376559686c66394971506f4353725a34453846664354413155506f4f6e4a7755493d")
fernet = Fernet(key)

#folder where the files will be saved after uploading from the admin portal
UPLOAD_FOLDER = 'uploads'

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )


app = Flask(__name__,template_folder="./templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
sess = Session()
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)













def testfunction(bookpdfname):


    print("test function calling ",bookpdfname)
    uploadfolder = os.path.join(app.config['UPLOAD_FOLDER'],bookpdfname)
    print('uploadfolder-->',uploadfolder)

    return send_file(uploadfolder,as_attachment=False)
    # return "success"



#route home api
# @app.route("/")
@app.route("/index")
def home():



    bookid = "midsem"
    session['currentBookId'] = bookid
    print('setting the values of session ', bookid)

    # print(' home print test function  BEFOREEEEE',bookpdfname)
    # hello = testfunction(bookpdfname)
    # print(' home print test function AFTERRRRRR ',bookpdfname)
    # print(hello)
    
    # path = 'midsem.pdf'
    # webbrowser.open_new(path)
    # filepath = '.../docs/midsem.pdf'
    # return send_from_directory(filepath, 'midsem.pdf')
    # send_from_directory
    # filetosend = 
    # uploadfolder = os.path.join(app.config['UPLOAD_FOLDER'],"midsem.pdf")
    # print('uploadfolder- - index --is---->',uploadfolder)
    # file = url_for('filename',bookname = 'midsem.pdf')
    # file = filename('temporarybookid.pdf')
    return render_template('index.html',filename = "midsefdgdfgm.pdf",pagenumber="2",file=url_for('filename'))
    # return render_template('index.html',filename = "midsemhfhfgh.pdf",pagenumber="2", file = send_file(uploadfolder,as_attachment=False))

#ROOT / LANDING Page
# @app.route("/")  
@app.route("/login",methods=['POST','GET'])
def login():
    username = ""
    password = ""
    msg=""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
        if username=="" or username==None:
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a username</b></p>'''
        elif password=="" or password==None:
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a password</b></p>'''
        else:
            dataBase = mysql.connector.connect(
            host ="localhost",
            user ="root",
            passwd ="",
            database = "bookdb"
            )
            cursorObject = dataBase.cursor(buffered=True) 
            sql = "SELECT username, password FROM user WHERE username='"+username+"'"
            cursorObject.execute(sql)
            result = cursorObject.fetchall()
            print(result)
            # xprint(fernet.decrypt(result[0][1].encode()).decode())
            if len(result)==0:
                msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Invalid username</b></p>'''
                dataBase.close()
                return render_template('login.html', message=msg)

            elif password!=fernet.decrypt(result[0][1].encode()).decode():
                msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Invalid password</b></p>'''
                dataBase.close()
                return render_template('login.html', message=msg)

            else:
                session['username']=username  
                return render_template('dashboard.html',username=username)

    return render_template('login.html', message=msg)






@app.route("/register",methods=['POST','GET'])
def register():
    name = ""
    username = ""
    email = ""
    password = ""
    msg=""
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if name=="":
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a valid name</b></p>'''
            return render_template('register.html', message=msg)
        elif username=="":
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a valid username</b></p>'''
            return render_template('register.html', message=msg)
        elif email=="":
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a valid email</b></p>'''
            return render_template('register.html', message=msg)
        elif password=="":
            msg='''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Enter a valid password</b></p>'''
            return render_template('register.html', message=msg)
        
        else:
            dataBase = mysql.connector.connect(
            host ="localhost",
            user ="root",
            passwd ="",
            database = "bookdb"
            )
            cursorObject = dataBase.cursor(buffered=True) 
            
            sql = "SELECT * FROM user WHERE username='"+username+"'"
            cursorObject.execute(sql)
            userexists = cursorObject.fetchall()
            if len(userexists)>0:
                msg = '''<p style="text-shadow: 2px; font-size: 20px; color: red;"><b>Username ['''+"'"+username+"'"+'''] is not available! Use a different username.</b></p>'''
                dataBase.close()
               
            else:
                enc_password = fernet.encrypt(password.encode())
                sql = "INSERT INTO user (username, name, email, password)\
                    VALUES(%s,%s,%s,%s)"
                val = (username, name, email, enc_password)
                cursorObject.execute(sql,val)
                dataBase.commit()
                # query = "SELECT * from user"
                # cursorObject.execute(query)
                # myresult = cursorObject.fetchall()
                msg = '''<p style="text-shadow: 2px; font-size: 20px; color: blue;"><b>User successfully created.
                Go to Login page to continue</b></p>'''
                dataBase.close()
    return render_template('register.html', message=msg)







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

    
    #after upload check if upload is successful or not
    msg = ""
    try:
        s3.upload_file(bookpdfpath, cred.S3_BUCKET,bookid+'.pdf', ExtraArgs=None, Callback=None, Config=None)

        response = s3.head_object(
            Bucket=cred.S3_BUCKET,
            Key=bookid+'.pdf',
        )
        print(response)
        msg = "Book Successfully Added"
    except ClientError as e:
        print("Error during upload: %s" % e)
        msg = "Error during Upload. Try Again !!"
        # if error then also delete that entry from booksdb

        
    return render_template("adminportal.html",message = msg)



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





@app.route("/")  
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
        tempdict['book_id'] = bookitem[0]
        tempdict['book_title'] = bookitem[1]
        tempdict['book_description'] = bookitem[3]
        blobimagedata =  base64.b64encode(bookitem[2])
        blobimagedata =blobimagedata.decode("UTF-8")
        tempdict['book_img'] = blobimagedata
        booksdata.append(tempdict)
    dataBase.close()
    # print(type(booksdata))
    # print(booksdata)

    # booksdata1 = [
    #     {"book_title": "book1","book_description": "book1 description ","book_img": "https://images.indianexpress.com/2022/12/Umar-Khalid.jpg"},
    #      {"book_title": "book2","book_description": "book2 description ","book_img": "https://c.ndtvimg.com/2022-12/g7nlvg58_3-killed-in-bomb-blast-at-trinamool-leaders-house_625x300_03_December_22.jpg"}
    #      ]
    return render_template("allbookspage.html",booksdata = booksdata)


@app.route("/filename")
def filename():
    if 'currentBookId' in session:
        currentBookId = session['currentBookId']
    
    print('book id in filename : ',currentBookId)
    bookPdfName = currentBookId+".pdf"
    # uploadfolder = app.config["UPLOAD_FOLDER"]
    # uploadfolder = os.path.join(app.config['UPLOAD_FOLDER'],bookPdfName)
    # path = ""
    downloadfolder = os.path.join("downloads",bookPdfName)
    print('download folder --->',downloadfolder)
    # print('uploadfolder-->',uploadfolder)
    session.pop('currentBookId') # unset this from UI when we click on home/logout/some back etc

    return send_file(downloadfolder,as_attachment=False)

#when all books clicked -> list of all books displayed
# when an individual book clicked
# the bookid is passed to this function


@app.route("/readnowfunction",methods=['GET','POST'])
def readnowfunction():
    bookid =request.form['readnowbookid']
    
    bookpdfname = bookid+".pdf"
    session['currentBookId'] = bookid
    pathto = 'downloads/'+bookpdfname
    #download bookpdfname from S3 and then open in online reader
    try:
        # s3bookpdffile = s3.Bucket(cred.S3_BUCKET).download_file(bookpdfname,bookpdfname)
        s3bookpdffile = s3.download_file(Bucket=cred.S3_BUCKET,Key=bookpdfname,Filename=pathto)
    except ClientError as e:
        print("Error during download: %s" % e)
        msg = "Error during Upload. Try Again !!"
        return render_template('dashboard.html',errormsg = "File Not Available")
    print(s3bookpdffile)

    #assuming we have downloaded the book from S3 in uploads folder for now
    pagenumber = "2"

    
    return render_template('reader.html',bookid=bookid,pagenumber=pagenumber,file=url_for('filename'))

@app.route("/mybooks",methods=['GET','POST'])
def mybooks():
    return render_template("mybookspage.html")

if __name__ == "__main__":
    # sess = Session()
    # sess.init_app(app)
    app.run(debug=True,port=5000)
