import os
import gc
from flask import Flask, render_template, url_for, flash, request, redirect, session
from db_connect import connection
from wtforms import Form, BooleanField, TextField, IntegerField, FormField, PasswordField, FileField, validators,MultipleFileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms.validators import Length
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps

app = Flask(__name__)
app.secret_key = "Top Secret!!!"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = './static/arac_fotolar/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

@app.route('/reset/')
def reset():
    c,conn=connection()
    c.execute("""CREATE TABLE IF NOT EXISTS user( user_Id INT AUTO_INCREMENT PRIMARY KEY,username varchar(30) NOT NULL,passwrd longtext NOT NULL,email nvarchar(50),role INT(5) NOT NULL,name NVARCHAR(30),lstname NVARCHAR(30),tc NVARCHAR(11),age INT,licanse_Age INT)""")
    conn.commit()
    c.close()
    conn.close()
    gc.collect()
    return redirect('homepage')

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/')
def homepage():
    return render_template("main.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Öncelikle giriş yapmalısınız!!!")
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            flash("Bu sayfa için yetkiniz bulunmamaktadır.")
            return redirect(url_for('homepage'))
    return wrap


@app.route('/adminlik_al/<username>')
@admin_required
def adminlik_al(username=''):
    c,conn = connection()
    print("Kullanıcıııı=  "+username)
    c.execute("""UPDATE user SET role=5 WHERE username='%s'"""%(username))
    conn.commit()
    c.close()
    conn.close()
    gc.collect()
    return redirect(url_for('uye_islemler'))
@app.route('/adminlik_ver/<username>')
@admin_required
def adminlik_ver(username=''):
    c,conn = connection()
    print("Kullanıcıııı=  "+username)
    c.execute("""UPDATE user SET role=1 WHERE username='%s'"""%(username))
    conn.commit()
    c.close()
    conn.close()
    gc.collect()
    return redirect(url_for('uye_islemler'))


@app.route("/admin_page/")
@login_required
@admin_required
def admin_page():
    return render_template("admin_page.html")


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("Başarı ile çıkış yaptınız.")
    gc.collect()
    return redirect(url_for('homepage'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    c,conn=connection()
    if request.method == 'POST':
        c.execute("""SELECT * FROM user WHERE email = '%s'"""%(request.form['email']))
        result=c.fetchall()
        usr=result[0][1]
        pas=result[0][2]
        role=result[0][4]
        if sha256_crypt.verify(request.form['password'],pas):
            session['logged_in']=True
            session['username']=usr
            if role==0:
                session['admin']=True
            elif role==1:
                session['admin']=True
            else:
                session['admin']=False
            gc.collect()
            return redirect(url_for('homepage'))
        else:
            flash("Hatalı giriş yaptınız. Tekrar deneyiniz.")
            return render_template("main.html")
    else:
        return redirect(url_for('homepage'))

class Kayitformu(Form):
    username= TextField('Kullanıcı Adı',[validators.Length(min=4,max=20)])
    password= PasswordField('Parola',[validators.Required(),validators.EqualTo('confirm',message="Passwords must match.")])
    confirm=PasswordField('Parola Tekrar')
    email= TextField('Email Adres',[validators.Length(min=10,max=50)])
    name= TextField('Ad',[validators.Length(min=0,max=20)])
    lstname= TextField('Soyad',[validators.Length(min=0,max=30)])
    tc= TextField('TC',[validators.Length(min=11,max=11)])
    age=IntegerField('Yaş')


@app.route('/register/', methods=['GET','POST'])
def register():
        if 'logged_in' in session:
            flash("Öncelikli çıkış yapmalısınız")
            return render_template("main.html")
        form = Kayitformu(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            role=5
            email= form.email.data
            name= form.name.data
            lstname= form.lstname.data
            tc= form.tc.data
            age= form.age.data
            licanse_Age=0
            c,conn = connection()
            sorgu="""SELECT COUNT(*) FROM user WHERE username = '%s'"""%(username)
            x=c.execute(sorgu)
            sonuc=c.fetchall()
            if sonuc[0][0]>0:
                flash("Bu kullanıcı adı kullanılmakta.")
                return render_template('register.html',form=form)
            else:
                #c.execute("INSERT INTO user(username, passwrd,role,name,lstname,tc,age,licanse_Age) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(thwart(username),thwart(password),thwart(role),thwart(name),thwart(lstname),thwart(tc),thwart(age),thwart(licanse_Age)))
                ekle_sorgu=("INSERT INTO user"
                         "(username,passwrd,email,role,name,lstname,tc,age,licanse_Age)"
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                sorgu_data=(thwart(username),thwart(password),email,role,name,lstname,tc,age,licanse_Age)
                c.execute(ekle_sorgu,sorgu_data)
                abc = c.fetchone()
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
                session['logged_in']=True
                session['username']=username
                return redirect(url_for('homepage'))
        return render_template("register.html",form=form)

class arac_form(Form):
    marka = TextField('Marka',[validators.Length(min=3,max=50)])
    model = TextField('Model',[validators.Length(min=3,max=50)])
    model_yil = IntegerField('Model Yıl')
    stok = IntegerField('Stok')
    ucret=IntegerField('Ücret')

@app.route('/arac_ekle/', methods=['GET','POST'])
@login_required
@admin_required
def arac_ekle():
    form = arac_form(request.form)
    if request.method == "POST" and form.validate():
        marka=form.marka.data
        model=form.model.data
        model_yil=form.model_yil.data
        stok=form.stok.data
        ucret=form.ucret.data
        c,conn = connection()

        ekle_sorgu=("INSERT INTO araclar"
                 "(marka,model,model_yil,stok,ucret)"
                 "VALUES (%s,%s,%s,%s,%s)")
        sorgu_data=(marka,model,model_yil,stok,ucret)
        c.execute(ekle_sorgu,sorgu_data)
        conn.commit()
        flash("Araç Başarı ile Eklendi")
        c.close()
        conn.close()
        gc.collect()
        return redirect(url_for('admin_page'))
    return render_template('arac_ekle.html',form=form)

@app.route('/arac_duzenle/')
@login_required
@admin_required
def arac_duzenle():
    c,conn = connection()
    sorgu=("SELECT * FROM araclar")
    c.execute(sorgu)
    rows=c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    gc.collect()
    return render_template('arac_duzenle.html',rows=rows)

@app.route('/arac_guncelle/<id>',methods=['GET','POST'])
@login_required
@admin_required
def arac_guncelle(id=0):
    c,conn = connection()
    sorgu="""SELECT * FROM araclar WHERE arac_Id = '%s'"""%(id)
    c.execute(sorgu)
    row=c.fetchall()
    if(request.method=='POST'):
        marka=request.form['marka']
        model=request.form['model']
        model_yil=request.form['model_yil']
        stok=request.form['stok']
        ucret=request.form['ucret']
        c,conn = connection()
        print("Güncellenecek= "+ stok)
        sorgu="""UPDATE araclar SET marka='%s',model='%s',model_Yil='%s',stok='%s',ucret='%s' WHERE arac_Id='%s'"""%(marka,model,model_yil,stok,ucret,id)
        c.execute(sorgu)
        conn.commit()
        c.close()
        conn.close()
        gc.collect()
        return redirect(url_for('arac_duzenle'))
    return render_template('arac_guncelle.html',row=row,id=id)

@app.route('/arac_listele/')
@app.route('/arac_listele/<error>/',methods=['GET','POST'])
@login_required
def arac_listele(id=0,error=0):
    if(error!=0):
        flash("Ne yazıkki bu araçtan stokta kalmadı :(")
        error=0
        return redirect(url_for('arac_listele'))
    c,conn = connection()
    sorgu=("SELECT * FROM araclar")
    c.execute(sorgu)
    rows=c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    gc.collect()
    if request.method=='POST':
        return redirect(url_for('arac_kirala'),id=id)
    return render_template("arac_listele.html",rows=rows)

@app.route('/arac_kirala/<id>',methods=['GET','POST'])
@login_required
def arac_kirala(id=0):
    c,conn = connection()
    sorgu="""SELECT * FROM araclar WHERE arac_Id = '%s'"""%(id)
    c.execute(sorgu)
    row=c.fetchall()[0]
    if(request.method=='POST'):
        gun=request.form['gun']
        tutar=int(gun)*row[5]
        return render_template("arac_kirala.html",row=row,flag=1,tutar=tutar,gun=gun)
    return render_template("arac_kirala.html",row=row,flag=0)

@app.route('/onay/<id>/<tutar>/<gun>/')
@login_required
def onay(id=0,tutar=0,gun=0):
    try:
        c,conn = connection()
        c.execute("""SELECT user_Id FROM user WHERE username='%s'"""%session['username'])
        user_Id=c.fetchone()[0]
        sorgu="""INSERT INTO kiralama_listesi (user_Id,arac_Id,gun,tutar) VALUES ('%s','%s','%s','%s') """%(user_Id,id,gun,tutar)
        c.execute(sorgu)

        c.execute("""SELECT stok-1 FROM araclar WHERE arac_Id='%s'"""%(id))
        stok=c.fetchone()[0]
        print("stok"+str(stok))

        c.execute("""UPDATE araclar SET stok='%s' WHERE arac_Id='%s'"""%(stok,id))
        conn.commit()
        c.close()
        conn.close()
        gc.collect()
        flash("Kiralama başarılı")
        return render_template("main.html")
    except:
        flash("Kiralama başarısız")
        return render_template("main.html")

@app.route('/islemler/')
@login_required
def islemler():
    c,conn = connection()
    c.execute("""SELECT user_Id FROM user WHERE username='%s'"""%session['username'])
    user_Id=c.fetchone()[0]
    c.execute("""SELECT kl.islem_Id,a.marka,a.model,a.model_Yil,a.ucret,kl.gun,kl.tutar FROM kiralama_listesi kl JOIN araclar a ON kl.arac_Id=a.arac_Id WHERE kl.user_Id=%s"""%(user_Id))
    rows=c.fetchall()
    c.execute("""SELECT SUM(tutar) FROM kiralama_listesi WHERE user_Id='%s'"""%(user_Id))
    toplam=c.fetchone()[0]
    c.close()
    conn.close()
    gc.collect()
    return render_template('islemler.html',rows=rows,toplam=toplam)

@app.route('/uye_islemler/')
@login_required
@admin_required
def uye_islemler():
    c,conn = connection()
    c.execute("""SELECT user_Id FROM user WHERE username='%s'"""%session['username'])
    user_Id=c.fetchone()[0]
    c.execute("""SELECT u.name,u.lstname,u.email,u.username,SUM(kl.tutar),u.user_Id FROM user u LEFT JOIN kiralama_listesi kl ON u.user_Id=kl.user_Id GROUP BY u.user_Id""")
    rows=c.fetchall()
    c.execute("""SELECT SUM(tutar) FROM kiralama_listesi""")
    toplam=c.fetchone()[0]
    c.close()
    conn.close()
    gc.collect()
    return render_template('uye_islemler.html',rows=rows,toplam=toplam)

@app.route('/uye_ayrinti/<id>/<toplam>/')
@login_required
@admin_required
def uye_ayrinti(id=0,toplam=0):
    c,conn = connection()
    c.execute("""SELECT u.username,u.email,u.name,u.lstname,u.tc,u.age,kl.islem_Id,kl.gun,kl.tutar,a.marka,a.model,a.model_Yil,a.ucret,u.role FROM user u JOIN kiralama_listesi kl ON u.user_Id=kl.user_Id JOIN araclar a ON kl.arac_Id=a.arac_Id WHERE u.user_Id=%s"""%(id))
    rows=c.fetchall()
    if int(rows[0][13])==1:
        return render_template('uye_ayrinti.html',rows=rows,role="Admin",flag=True)
    elif int(rows[0][13])==5:
        return render_template('uye_ayrinti.html',rows=rows,role="Üye",flag=False)
    else:
        return render_template('uye_ayrinti.html',rows=rows,role="Root",flag=True)

if __name__ == '__main__':
    app.run(debug=True)
