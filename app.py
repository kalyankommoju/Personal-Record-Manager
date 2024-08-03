from flask import Flask,render_template,request,redirect,url_for,flash,session,send_file
from flask_session import Session
import flask_excel as excel
import mysql.connector
from otp import genotp
from cmail import sendmail
from io import BytesIO
import re
mydb=mysql.connector.connect(host='localhost',user='root',password='kalyan',db='prm')
app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
Session(app)
excel.init_excel(app)
app.secret_key='kalyan'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/registration',methods=['GET','POST'])
def register():
    if request.method=='POST':
        print(request.form)
        username=request.form['name']
        password=request.form['password']
        email=request.form['email']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from register where username=%s',[username])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from register where email=%s',[email])
        count2=cursor.fetchone()[0]
        cursor.close()
        print(count)
        print(count2)
        if count==0:
            if count2==0:
                otp=genotp()
                subject='Thanks for registering'
                body=f'You this otp regiseter {otp}'
                sendmail(email,subject,body)
                print(otp)
                flash('OTP has send your Email')
                return render_template('otp.html', username=username, password=password, email=email, otp=otp)
            else:
                flash('email is alredy existed')
                return render_template('register.html')
        else:
            flash('username is alredy existed')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/otp/<username>/<password>/<email>/<otp>',methods=['GET','POST'])
def verify(username,password,email,otp):
    if request.method=='POST':
        otp1=request.form['otp']
        if otp1==otp:
            print('OTP is verify')
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into register (username,password,email) value (%s,%s,%s)',[username,password,email])
            mydb.commit()
            cursor.close()
            flash('registertion is completed')
            return redirect(url_for('login'))
        else:
            flash('OTP was incorrect')
            return redirect(url_for('verify'))
    return render_template('otp.html',username=username,password=password,email=email,otp=otp)

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('homepage'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select  count(*) from register where username=%s and password=%s',[username,password])
        var1=cursor.fetchone()[0]
        cursor.close()
        if var1==1:
            session['user']=username
            flash('Your login is completed')
            return redirect(url_for('homepage'))
        else:
            flash('Plz enter correct password')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    
@app.route('/homepage')
def homepage():
    if session.get('user'):
        return render_template('home.html')
    else:
        return redirect(url_for('home'))
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            user=session.get('user')
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into notes (title,content,username) values (%s,%s,%s)',[title,content,user])
            mydb.commit()
            cursor.close()
            flash('Your notes has inserted')
            return render_template('home.html')
        return render_template('addnotes.html')
    return redirect(url_for('login'))

@app.route('/allnotes')
def allnotes():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select notes_id,title from notes where username=%s',[session.get('user')])
        data=cursor.fetchall()
        cursor.close()
        return render_template('allnotes.html',data=data)
    return render_template('allnotes.html')

@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select title,content from notes where notes_id=%s',[nid])
        view=cursor.fetchall()
        cursor.close()
        return render_template('viewnotes.html',view=view)
    return redirect(url_for('login'))


@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):
    if session.get('user'):
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select title,content from notes where notes_id=%s',[nid])
            update=cursor.fetchall()
            cursor.close()
            if request.method=='POST':
                title1=request.form['title1']
                content1=request.form['content1']
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update notes  set title=%s ,content=%s where notes_id=%s',[title1,content1,nid])
                mydb.commit()
                cursor.close()
                flash(f'notes with id{nid} updated')
                return redirect(url_for('allnotes'))
            return render_template('updatenotes.html',update=update)
    return redirect(url_for('login'))

@app.route('/deletenotes/<nid>')
def deletenotes(nid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('delete from notes where notes_id=%s',[nid])
        mydb.commit()
        cursor.close()
        return redirect(url_for('allnotes'))
    return redirect(url_for('login'))

@app.route('/search',methods=['GET','POST'])
def search():
    if session.get('user'):
        if request.method=='POST':
            search=request.form['search']
            strg=['A-Za-z0-9']
            pattern=re.compile(f'^{strg}',re.IGNORECASE)
            if pattern.match(search):
                cursor=mydb.cursor(buffered=True)
                cursor.execute('select notes_id,title from notes where username=%s and title LIKE %s', [session.get('user'),search + '%'])
                data1=cursor.fetchall()
                cursor.close()
                return render_template('home.html',items=data1)
            else:
                flash('result not found')
                return redirect(url_for('homepage'))
    return redirect(url_for('login'))

@app.route('/getdata')
def getdata():
    if session.get('user'):
        username=session.get('user')
        cursor=mydb.cursor(buffered=True)
        columns=['Title','Content']
        cursor.execute('select title,content from notes where username=%s',[username])
        data=cursor.fetchall()
        print(data)
        cursor.close()
        array_data=[list(i) for i in data]
        print(array_data)
        array_data.insert(0,columns)
        print(array_data)
        return excel.make_response_from_array(array_data,'xlsx', filename='notesdata')
    else:
        return redirect(url_for('login'))
    
@app.route('/uploadfile', methods=["GET","POST"])
def uploadfile():
    if session.get('user'):
        if request.method=='POST':
            files=request.files.getlist('file')
            username=session.get('user')
            cursor=mydb.cursor(buffered=True)
            for file in files:
                print(file)
                file_ext=file.filename.split('.')[-1]
                file_data=file.read()
                cursor.execute('insert into files(extension,file_data,username) values (%s,%s,%s)',[file_ext,file_data,username])
                mydb.commit()
            cursor.close()
            flash('files upload successfully')
            return redirect(url_for('homepage'))
        return render_template('uploadfile.html')
    return redirect(url_for('login'))
@app.route('/allfiles')
def allfiles():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select fid from files where username=%s',[session.get('user')])
        data=cursor.fetchall()
        cursor.close()
        return render_template('viewfiles.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/viewfile/<fid>')
def viewfile(fid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select extension,file_data from files where fid=%s',[fid])
        ext,bin_data=cursor.fetchone()
        bytes_data=BytesIO(bin_data)
        filename=f'attachment.{ext}'
        return send_file(bytes_data,download_name=filename,as_attachment=False)
    else: 
        return redirect(url_for('login'))

@app.route('/downloadfile/<fid>')
def downloadfile(fid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select extension,file_data from files where fid=%s',[fid])
        ext,bin_data=cursor.fetchone()
        bytes_data=BytesIO(bin_data)
        filename=f'attachment.{ext}'
        return send_file(bytes_data,download_name=filename,as_attachment=True)
    else:
        return redirect(url_for('login'))

@app.route('/deletefile/<fid>')
def deletefile(fid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('delete from files where fid=%s',[fid])
        mydb.commit()
        cursor.close()
        return redirect(url_for('allfiles'))
    return redirect(url_for('login'))

app.run(debug=True,use_reloader=True)