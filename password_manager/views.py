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
    error_flag = False

def getrows(request):
    dt = {}
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.execute(f"SELECT * FROM {request.session['username']} where id <> 0 order by id asc")
        txt = "{:5}{:<25}{:<20}{:<20}".format("ID", "SITE", "USERNAME", "PASSWORD")
        print(txt)
        '''for row in cursor:
            txt += "\n{:<5}{:<25}{:<20}{:<20}".format(row[0],row[1],row[2],"********")
            print(txt)'''
        dt["db_rows"] = list(cursor)

    print("Getting rows...............................")
    unhidden = request.session.get('unhidden', [])

    print("UNhidden..................",unhidden)
    for i in range(0,len(dt["db_rows"])):
        dt["db_rows"][i] = list(dt["db_rows"][i])
        if dt["db_rows"][i][0] not in unhidden:
            dt["db_rows"][i][3] = "********"
        else:
            key = request.session['password']
            if len(key) > 32:
                key = key[0:32]
            elif len(key) < 32:
                key = key + (32 - len(key))*"0"
            print(key,dt["db_rows"][i][3])
            password = decrypt(key,dt["db_rows"][i][3])
            dt["db_rows"][i][3] = password.decode('utf-8')
    print(dt)
    return dt

def addrecord(id,site,username,password,request):
    key = request.session['password']
    if len(key) > 32:
        key = key[0:32]
    elif len(password) < 32:
        key = key + (32 - len(key))*"0"
    token = encrypt(key,password)
    with sqlite3.connect('db.sqlite3') as conn:
        query = f'''INSERT INTO {request.session['username']} VALUES({id},"{site}","{username}","{token.decode('utf-8')}")'''
        print(query)
        conn.execute(query)
        conn.commit()
        print("Record Inserted Successfully")

def homepage(request):
    
    #if session already saved
    if request.session.has_key('username'):
        print("\nSession was Saved")
        dt = getrows(request)
        data={
            "title" : "Password Manager"
        }
        to_match=""
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.execute(f"SELECT password FROM {request.session['username']} where ID=0")
            to_match= list(cursor)[0][0]
            print(to_match,type(to_match))
        if bcrypt.checkpw(request.session['password'].encode("utf-8"),to_match.encode("utf-8")):
            print("\nPassword Correct")
            dt = getrows(request)
            data={
                "title" : "Password Manager",
                "username" : request.session['username']
            }
            return render(request,"index.html",dt)
        else:
            del request.session['username']
            messages.error(request, 'Wrong Password!')
            return render(request,"login.html")
    else:
        return render(request,"login.html")

def viewrecord(request):
    print("In view Record")
    if request.method == 'POST':
        id = request.POST.get('id')
        id=int(id)
    if id !=0 : 
        my_list = request.session.get('unhidden', [])
        print("my_list before",my_list)
        my_list.append(id)
        request.session['unhidden'] = my_list
        print("my_list",my_list)
            
    print(request.session['unhidden'],'------------------')
    return redirect('/')

def checklogin(request):
    if request.method == 'POST':
        request.session['username'] = request.POST.get('master_username')
        request.session['password'] = request.POST.get('master_password')
        name = request.session['username']
        print(request.session['password'],request.session['password'])
        if table_exists(name):
            return redirect('/')
        else:
            messages.error(request, 'No USER Found!')
            return render(request,"login.html")
            
    else:
        return render(request,"login.html")
     
def table_exists(table_name):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        
        if result:
            return True
        else:
            return False

def aboutus(request):
     return render(request,"about.html")
def logout(request):
    print("-----------------------In request logout------------")
    print(request.method)
    del request.session['username']
    del request.session['password']
    deleted_value = request.session.pop('unhidden', None)
    request.session.save()
    print("in logout ....................")
    return redirect('/')

def hideall(request):
    deleted_value = request.session.pop('unhidden', None)
    request.session.save()
    print("in logout ....................")
    return redirect('/')


def deleterecord(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id=int(id)
        if(id == 0):
            messages.error(request, 'Cannot Delete master password')
            return redirect('/')
        print('-------------- ',id,type(id))
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.execute(f"SELECT * FROM {request.session['username']} where id={id}")
            if len(list(cursor)) == 0:
                print("NO Record with such ID")
                messages.error(request, 'NO Record with such ID')
            else:
                cursor = conn.execute(f"DELETE FROM {request.session['username']} where id={id}")
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
        cursor = conn.execute(f"SELECT * FROM {request.session['username']} where id={id}")
        if len(list(cursor)) == 0:
            print("NO Record with such ID")
            messages.error(request, 'NO Record with such ID')
        else:
            key = request.session['password']
            if len(key) > 32:
                key = key[0:32]
            elif len(password) < 32:
                key = key + (32 - len(key))*"0"
            token = encrypt(key,password)
            cursor = conn.execute(f'''UPDATE {request.session['username']} SET SITE="{site}",username="{username}",password="{token.decode('utf-8')}" where id={id}''')
            conn.commit()
    return redirect('/')
    

def register(request):
    if request.method == 'POST':
        request.session['username'] = request.POST.get('master_username')
        request.session['password'] = request.POST.get('master_password')
        name = request.session['username']
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.execute(f"SELECT name from sqlite_master where type='table' and name='{name}'")
            result = cursor.fetchone()
            if result:
                print("USER EXISTS")
                messages.error(request, 'USER ALREADY EXISTS!')
                return render(request,'register.html')
        print(request.session['username'],request.session['password'])
        create_table(name)
        pwd_bytes = request.session['password'].encode("utf-8")
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(pwd_bytes, salt)
        with sqlite3.connect('db.sqlite3') as conn:
            query = f'''INSERT INTO {request.session['username']} VALUES(0,"master","master","{pwd_hash.decode('utf-8')}");'''
            conn.execute(query)
            conn.commit()
            print("Master Password Set Successfully , Remember it !")
        return redirect('/')
    else:
        return render(request,'register.html')
    


def saverecord(request):
    if request.method == 'POST':
        site = request.POST.get('site')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(site,username,password)
    id=0
    query = f'''select id from {request.session['username']} order by id desc limit 1;'''
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.execute(query)
        lst = list(cursor)
        id = lst[0][0] + 1
    addrecord(id,site,username,password,request)
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

def create_table(name):
    with sqlite3.connect('db.sqlite3') as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {name}
            (ID INT PRIMARY KEY NOT NULL,
            SITE  TEXT NOT NULL,
            USERNAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL);
        ''')