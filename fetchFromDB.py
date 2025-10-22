from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = None # Dopln lokalne
db = SQLAlchemy(app)

class Word(db.Model):
    __tablename__ = 'hangman_words'  # or whatever your table name is
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

@app.route('/hangman/penalties')
def index():
    words = Word.query.all()
    print("Im here")
    print(words)
    if not words:
        print("No data found!")
    else:
        for w in words:
            print(w.content)
    return render_template('hangman.html', words=words)