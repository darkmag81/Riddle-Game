import os
import json

from flask import Flask, redirect, render_template, request

app = Flask(__name__)
app.secret_key = 'some_secret'
data = []

def saveToFile(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

def addBadAnswers(username, message):
    saveToFile("data/badanswers.txt", "({0}) - {1}\n".format(
            username.title(),
            message))

def getBadAnswers():
    answer = []
    with open("data/badanswers.txt", "r") as badAnswers:
        answer = [row for row in badAnswers if len(row.strip()) > 0]
    return answer

def getAllPlayers():
    users = []
    with open("data/playersList.txt", "r") as playerAnswer:
        users = playerAnswer.readlines()
    return users

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        saveToFile("data/playersList.txt", request.form["username"] + "\n")
        return redirect(request.form["username"])
    return render_template("index.html")

@app.route('/<username>', methods=["GET", "POST"])
def user(username):
    wrongAnswersText = ''
    wrongAnswersList = ''
    data = []
    with open("data/riddles.json", "r") as json_data:
        data = json.load(json_data)
    rIndex = 0
    if request.method == "POST":
        rIndex = int(request.form["rIndex"])
        playerAnswer = request.form["message"].lower()
        if data[rIndex]["answer"] == playerAnswer:
            rIndex += 1
            wrongAnswersText = ''
            wrongAnswersList = ''
        else:
            addBadAnswers(username, playerAnswer + "\n")
            wrongAnswersText = 'Wrong Answers:'
            wrongAnswersList = wrongAnswersList + playerAnswer
    if request.method == "POST":
        if playerAnswer == "secretanswer12" and rIndex > 10:
            return render_template("end.html", username=username)
    answer = getBadAnswers()
    return render_template("riddle.html", username=username, badAnswers=answer, riddles_data=data, rIndex=rIndex, wrongAnswersText=wrongAnswersText, wrongAnswersList=wrongAnswersList)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)