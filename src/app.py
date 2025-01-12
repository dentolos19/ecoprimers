from App import app
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# create flask instance 
app = Flask(__name__)

# # Add Database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# # Initialise the database 
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# # create model 
# class Users(db.Model):
#     id = db.Column(db.Integer, primary_key = True) #primarykey is unqie 
#     name = db.Column(db.String(200), nullable = False) #nullable meaning cnnt be blank 
#     email = db.Column(db.String(200), nullable = False, unqie = True)
#     date_added = db.Column(db.DateTime, default=datetime.utcnow)

#     # create a string 
#     def __repr__(self):
#         return '<Name %r>' % self.name

# create a blog post model 
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    slug = db.Column(db.String(255))



if __name__ == "__main__":
    # Debug mode will be set via the environment variable (FLASK_DEBUG)
    app.run(debug=1)


    