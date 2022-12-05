from flask import Flask,render_template,request,redirect,url_for


app = Flask(__name__,template_folder="./templates")


#route home api
@app.route("/")
@app.route("/index.html")
def home():
 return render_template('index.html')

@app.route("/register.html")
def register():
 return render_template('register.html')



if __name__ == "__main__":
 app.run(debug=True,port=5000)
