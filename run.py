import os
import json
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'secretpassword'

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(request.form["username"]))    
    return render_template("index.html",  page_title="Riddle Game")

@app.route('/riddle')
def riddle():
    data = []
    with open("data/riddles.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("riddle.html", page_title="Riddle Game - Riddles", company_data=data)

@app.route('/riddle/<riddle_no>')
def riddlePage(riddle):
    member = {}
    
    with open("data/riddles.json", "r") as json_data:
        data = json.load(json_data)
        for obj in data:
            if obj["url"] == riddle:
                member = obj
                
    return render_template("member.html", member=member)

@app.route('/end')
def endGame():
    return render_template("end.html", page_title="Riddle Game - Game Over")

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)