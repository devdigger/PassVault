from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
import sqlite3
import os,bcrypt
from cryptography.fernet import Fernet
import base64

class Vars:
    masterpass = ""
    unhidden = []

def getrows():
    dt = {}
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.execute("SELECT * FROM PASSWORDS where id <> 0 order by id asc")
        txt = "{:5}{:<25}{:<20}{:<20}".format("ID", "SITE", "USERNAME", "PASSWORD")
        print(txt)
        '''for row in cursor:
            txt += "\n{:<5}{:<25}{:<20}{:<20}".format(row[0],row[1],row[2],"********")
            print(txt)'''
        dt["db_rows"] = list(cursor)
    for i in range(0,len(dt["db_rows"])):
        dt["db_rows"][i] = list(dt["db_rows"][i])
        if dt["db_rows"][i][0] not in Vars.unhidden:
            dt["db_rows"][i][3] = "********"
        else:
            key = Vars.masterpass
            if len(key) > 32:
                key = key[0:32]
            elif len(key) < 32:
                key = key + (32 - len(key))*"0"
            password = decrypt(key,dt["db_rows"][i][3])
            dt["db_rows"][i][3] = password.decode('utf-8')
    print(dt)
    return dt

def addrecord(id,site,username,password):
    key = Vars.masterpass
    if len(key) > 32:
        key = key[0:32]
    elif len(password) < 32:
        key = key + (32 - len(key))*"0"
    token = encrypt(key,password)
    with sqlite3.connect('db.sqlite3') as conn:
        query = f'''INSERT INTO PASSWORDS VALUES({id},"{site}","{username}","{token.decode('utf-8')}")'''
        print(query)
        conn.execute(query)
        conn.commit()
        print("Record Inserted Successfully")

def savemasterpass(request):
    if request.method == 'POST':
        print("in save master password function")
        Vars.masterpass = request.POST.get('master_password')
        print(Vars.masterpass)
        pwd_bytes = Vars.masterpass.encode("utf-8")
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(pwd_bytes, salt)
        with sqlite3.connect('db.sqlite3') as conn:
            query = f'''INSERT INTO PASSWORDS VALUES(0,"master","master","{pwd_hash.decode('utf-8')}");'''
            conn.execute(query)
            conn.commit()
            print("Master Password Set Successfully , Remember it !")
        return redirect('/')

def homepage(request):
    create_table()
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.execute("SELECT * FROM PASSWORDS where ID=0")
        if len(list(cursor)) == 0:
            print("No Master password exists")
            return render(request,'create-masterpassword.html')
    if Vars.masterpass == "":
        return render(request,"login.html")
    to_match=""
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.execute("SELECT password FROM PASSWORDS where ID=0")
        to_match= list(cursor)[0][0]
        print(to_match,type(to_match))
    if bcrypt.checkpw(Vars.masterpass.encode("utf-8"),to_match.encode("utf-8")):
        print("\nPassword Correct")
        dt = getrows()
        data={
            "title" : "Password Manager"
        }
        return render(request,"index.html",dt)
    else:
        messages.error(request, 'Wrong Password!')
        return render(request,"/login/")

def viewrecord(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id=int(id)
    if id !=0 : Vars.unhidden.append(id)
    print(Vars.unhidden,'------------------')
    return redirect('/')

def checklogin(request):
    if request.method == 'POST':
        Vars.masterpass = request.POST.get('master_password')
        print(Vars.masterpass)
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.execute("SELECT * FROM PASSWORDS where ID=0")
        if len(list(cursor)) == 0:
            print("No Master password exists")
            return render(request,'create-masterpassword.html') 
    return redirect('/')
     


def aboutus(request):
     return render(request,"about.html")


def deleterecord(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id=int(id)
        if(id == 0):
            messages.error(request, 'Cannot Delete master password')
            return redirect('/')
        print('-------------- ',id,type(id))
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.execute(f"SELECT * FROM PASSWORDS where id={id}")
            if len(list(cursor)) == 0:
                print("NO Record with such ID")
                messages.error(request, 'NO Record with such ID')
            else:
                cursor = conn.execute(f"DELETE FROM PASSWORDS where id={id}")
                conn.commit()
    return redirect('/')

def editrecord(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id=int(id)
        site = request.POST.get('site')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(id,site,username,password)
        if(id == 0):
            messages.error(request, 'Cannot edit master password')
            return redirect('/')
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.execute(f"SELECT * FROM PASSWORDS where id={id}")
        if len(list(cursor)) == 0:
            print("NO Record with such ID")
            messages.error(request, 'NO Record with such ID')
        else:
            key = Vars.masterpass
            if len(key) > 32:
                key = key[0:32]
            elif len(password) < 32:
                key = key + (32 - len(key))*"0"
            token = encrypt(key,password)
            cursor = conn.execute(f'''UPDATE PASSWORDS SET SITE="{site}",username="{username}",password="{token.decode('utf-8')}" where id={id}''')
            conn.commit()
    return redirect('/')

def saverecord(request):
    if request.method == 'POST':
        site = request.POST.get('site')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(site,username,password)
    id=0
    query = '''select id from passwords order by id desc limit 1;'''
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.execute(query)
        lst = list(cursor)
        id = lst[0][0] + 1
    addrecord(id,site,username,password)
    return redirect('/')

def encrypt(password,data):
    key = bytes(password,'utf-8')
    key = base64.b64encode(key)
    
    f = Fernet(key)
    
    # the plaintext is converted to ciphertext
    token = f.encrypt(data.encode('utf-8'))
    return token

def decrypt(password,token):
    key = bytes(password,'utf-8')
    key = base64.b64encode(key)
    #print(key)  
    # value of key is assigned to a variable
    f = Fernet(key)
    d = f.decrypt(token)
    return d

def create_table():
    with sqlite3.connect('db.sqlite3') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS PASSWORDS
            (ID INT PRIMARY KEY NOT NULL,
            SITE  TEXT NOT NULL,
            USERNAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL);
        ''')