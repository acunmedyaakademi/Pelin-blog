from flask import Flask, jsonify,request,redirect, url_for
from functions import *
#from functions import signup,get_users,login,add_blogpost,get_blogposts,get_one_post,edit_post,get_one_column,delete_post,post_comment,read_post_comments
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app= Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

@app.route("/signup", methods=["POST"])
def signup_():
    username = request.form['username']
    password = request.form['password'] 
    return signup(username,password)
  
@app.route("/users")
def get_users_():
    return get_users()  

@app.route("/login", methods=["POST"])
def login_():
    username = request.form['username']
    password = request.form['password']
    return login(username,password)

@app.route("/add-post", methods=["POST"])
@jwt_required()
def add_post():
    
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    userid = get_jwt_identity()
    return add_blogpost(title,summary,content,userid)

@app.route("/posts")

def get_posts():
    return get_blogposts()

@app.route("/posts/<id>")
def get_post(id):
    return get_one_post(id)

@app.route("/update-post/<id>", methods=["POST"])
@jwt_required()
def update_post(id):
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    userid = get_jwt_identity()
    return edit_post(id,title,summary,content,userid)

@app.route("/delete-post/<id>")
@jwt_required()
def remove_post(id):
    userid = get_jwt_identity()
    return delete_post(id,userid)

@app.route('/<post_id>/comments/post',methods=["POST"])
@jwt_required()
def post_comment_(post_id):
    comment=request.form['comment']
    return post_comment(comment,post_id,get_jwt_identity())
    
    
@app.route('/<post_id>/comments')
def read_post_comments_(post_id):
    return read_post_comments(post_id)
    

@app.route("/comments/delete/<comment_id>")
@jwt_required()
def delete_comment_(comment_id):
    userid=get_jwt_identity()
    return delete_comment(comment_id,userid)

@app.route('/comments/update/<comment_id>',methods=["POST"])
@jwt_required()
def update_comment_(comment_id):
    comment=request.form['comment']
    return edit_comment(comment_id,comment,get_jwt_identity())
    




if __name__ == "__main__":
    app.run()