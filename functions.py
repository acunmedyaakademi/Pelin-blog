import sqlite3
from flask import jsonify
import datetime
import hashlib
from flask_jwt_extended import create_access_token
import re

def signup(username='',password=''):
    if username == "" or password == "":
        return jsonify({"message":"Username or password is empty"})
    if len(password) < 7:
        return jsonify({"message":"Password must be at least 7 characters long"})
    if not re.search(r'\d', password):
        return jsonify({"message":"Password must contain at least one number"})
    
    conn = sqlite3.connect('BlogDb.db')
    cursor = conn.cursor()
    created_on = datetime.datetime.now()
    password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username,password,created_on) VALUES(?,?,?)", (username,password,created_on))
    conn.commit()
    conn.close()
    return jsonify({"message":"Account created"})


def db_get_data(query,params=()):
    conn = sqlite3.connect('BlogDb.db')
    cursor=conn.cursor()
    cursor.execute(query,params)
    data=cursor.fetchall()
    conn.close()
    return data

def get_one_column(table_name,column_name,id):
    conn = sqlite3.connect('BlogDb.db')
    cursor=conn.cursor()
    cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE id=?", (id,))
    data =cursor.fetchone()
    return data[0]
       
    
def db_get_formatted_data(query,params=()):
    conn = sqlite3.connect('BlogDb.db')
    cursor=conn.cursor()
    cursor.execute(query,params)
    data=cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    formatted_data = []
    for row in data:
        row_dict = dict(zip(column_names, row))
        formatted_data.append(row_dict)
    conn.close()
    return formatted_data

    
def db_commit(query,params=()):
    conn = sqlite3.connect('BlogDb.db')
    cursor=conn.cursor()
    cursor.execute(query,params)
    conn.commit()
    if cursor.rowcount < 1:
        conn.close()
        return False
    conn.close()
    return True
    
def get_users():
    query = "SELECT id,username, created_on FROM users"
    return jsonify(db_get_data(query))

def login(username='',password=''):
    if username == "" or password == "":
        return jsonify({"message":"Username or password is empty"})    
    password = hashlib.sha256(password.encode()).hexdigest()
    query = "SELECT COUNT(id) FROM users WHERE username=? AND password=?"
    userid = db_get_data('SELECT id FROM users WHERE username=? AND password=?',(username,password))[0][0]
    params = (username,password)
    if db_get_data(query,params)[0][0] > 0:
        return jsonify({"message":"Login successful, please use the token for future requests",
                        'Access Token': create_access_token(identity=userid)
                        })
    
    else:
        return jsonify({"message":"Login failed, username or password is incorrect"})
    
def add_blogpost(title='',summary='',content='',userid=''):
    if title == "" or content == "" :
        return jsonify({"message":"please enter a title and content"})
    created_on = datetime.datetime.now()
    query = "INSERT INTO posts (user_id,title,summary,content,created_on) VALUES(?,?,?,?,?)"
    params = (userid,title,summary,content,created_on)
    commit =db_commit(query,params)
    if commit == True:
        return jsonify({"message":"Blog post added"})
    
def get_blogposts():
    query = "SELECT posts.id,posts.title,posts.summary,posts.created_on, users.username, posts.updated_on FROM posts INNER JOIN users ON posts.user_id = users.id" 
    conn = sqlite3.connect('BlogDb.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    formatted_data = []
    for row in data:
        row_dict = dict(zip(column_names, row))
        formatted_data.append(row_dict)

    conn.close()

    return jsonify(formatted_data)

def get_one_post(id=''):
    if id == "":
        return jsonify({"message":"please enter a post id"})
    query = "SELECT posts.id,posts.title,posts.summary,posts.content,posts.created_on,posts.updated_on,users.username FROM posts INNER JOIN users ON posts.user_id = users.id WHERE posts.id=?"
    params = (id,)
    conn = sqlite3.connect('BlogDb.db')
    cursor = conn.cursor()
    cursor.execute(query,params)
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    formatted_data = []
    for row in data:
        row_dict = dict(zip(column_names, row))
        formatted_data.append(row_dict)
    conn.close()
    return jsonify(formatted_data)

    
def edit_post(id,title='',summary='',content='',userid=''):
    if not title or title == "":
        title =db_get_data("SELECT title FROM posts WHERE id=?",(id,))[0][0]
    if not summary or summary == "":
        summary =db_get_data("SELECT summary FROM posts WHERE id=?",(id,))[0][0]
    if not content or content == "":
        content =db_get_data("SELECT content FROM posts WHERE id=?",(id,))[0][0]    
    updated_on = datetime.datetime.now()         
    query = "UPDATE posts SET title=?,summary=?,content=?, updated_on=? WHERE id=? AND user_id=?"
    params = (title,summary,content,updated_on,id,userid)
    commit =db_commit(query,params)
    if commit == True:
        data=db_get_formatted_data("SELECT title,summary,content,updated_on FROM posts WHERE id=?",(id,)) 
        return jsonify({"message":"Blog post updated",
                        "post":data})
    else:
        return jsonify({"message":"Blog post cannot be updated"})
    
def delete_post(id='',userid=''):
    comm=db_commit("DELETE FROM posts WHERE id=? AND user_id=?",(id,userid))
    if comm == True:
        return jsonify({"message":"Post deleted"})
    else:
        return jsonify({"message":"Post cannot be deleted"})
    
    
def post_comment(comment,post_id='',user_id=''):
    created_on = datetime.datetime.now()
    query = "INSERT INTO comments (comment,post_id,userid,created_on) VALUES(?,?,?,?)"
    params = (comment,post_id,user_id,created_on)
    commit =db_commit(query,params)
    if commit == True:
        return jsonify({"message":"Comment added"})
    else:
        return jsonify({"message":"Comment cannot be added"})
    

def read_post_comments(post_id):
    query="SELECT comments.id,comments.comment,comments.created_on,users.username FROM comments INNER JOIN users ON comments.userid = users.id WHERE comments.post_id=?"
    params = (post_id,)
    return jsonify(db_get_formatted_data(query,params))
    
    
def delete_comment(comment_id,user_id):
    query="DELETE FROM comments WHERE id=? AND userid=?"
    params=(comment_id,user_id)
    commit=db_commit(query,params)
    if commit == True:
        return jsonify({"message":"Comment deleted"})
    else:
        return jsonify({"message":"Comment cannot be deleted"})
    
    
def edit_comment(comment_id,comment,user_id):
    updated_on = datetime.datetime.now()
    query="UPDATE comments SET comment=?,updated_on=? WHERE id=? AND userid=?"
    params=(comment,updated_on,comment_id,user_id)
    commit=db_commit(query,params)
    if commit == True:
        return jsonify({"message":"Comment updated"})
    else:
        return jsonify({"message":"Comment cannot be updated"})
    
    

    

        
    