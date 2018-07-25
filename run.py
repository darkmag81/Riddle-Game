import os
import json
import datetime

from flask import Flask, redirect, render_template, request, flash

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'some_secret'
data = []
with open("data/highscore.json", "r") as json_data:
    player = json.load(json_data)
    json_data.close()    
        
def saveToFile(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

def addBadAnswers(username, message, index, lives):
    if not message:
        answer = "No answer"
    else:
        answer = message
    message_to_save = "Riddle " + str(index +1) + ", tries left " + str(lives) + ": " + answer + "\n"
    saveToFile("data/badanswers.txt", "({0}) - {1}".format(username.title(), answer + "\n"))
    file_name = "data/" + username + ".txt"
    saveToFile(file_name, message_to_save)

def highscoreUpdate(score, username):
    with open("data/highscore.json", "r") as json_data:
        player = json.load(json_data)
        for x in range (0,len(player)):
            if score > int(player[x]["score"]):
                newRecord = {"name": username, "score": score}
                player.append(newRecord)
                break
    sorted_player = sorted(player, key=lambda k: k['score'], reverse=True)
    while len(sorted_player) > 5:
        del sorted_player[5]
    with open('data/highscore.json', 'w') as outfile:
        json.dump(sorted_player, outfile)
        outfile.close()

@app.route('/', methods=["GET", "POST"])
def index():
    span_text = ""
    if request.method == "POST":
        file_name = "data/" + request.form["username"] + ".txt"
        if not os.path.exists(file_name):
            saveToFile(file_name, "Player created on " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" +
            "-------------------------------------------\n" + "Bad answers list:\n" +
            "-------------------------------------------\n")
            saveToFile("data/playersList.txt", request.form["username"] + "\n")
            return redirect(request.form["username"])
        span_text = request.form["username"] + " is already taken... Please choose different one"
        return render_template("index.html", span_text=span_text, player=player)
    return render_template("index.html", player=player)

@app.route('/<username>', methods=["GET", "POST"])
def user(username):
    wrongAnswersText = ''
    data = []
    rIndex = 0
    score = 0
    tries = 1
    with open("data/riddles.json", "r") as json_data:
        data = json.load(json_data)
    if request.method == "POST":
        rIndex = int(request.form["rIndex"])                    # get index
        score = int(request.form["score"])                      # get score
        tries = int(request.form["tries"])                      # get remaining tries
        playerAnswer = request.form["message"].lower()          # make answer lowercase
        if data[rIndex]["answer"] == playerAnswer:              # correct answer
            rIndex += 1
            score += 1
            tries = 1
            wrongAnswersText = ''
            if rIndex >= len(data):                             # if answered last riddle go to end.html
                file_name = "data/" + username + ".txt"
                saveToFile(file_name, "-------------------------------------------\nScore: " + str(score) + "\n-------------------------------------------")
                highscoreUpdate(score, username)
                return render_template("end.html", 
                       username=username, score=score, player=player)
        else:                                                   # wrong answer
            addBadAnswers(username, playerAnswer, rIndex, tries)# add wrong answer to file
            if tries >= 1:                                      # if there is one or  more tries available
                tries -= 1
                wrongAnswersText = '"' + playerAnswer + '" is wrong! Please try one more time...'
                return render_template("riddle.html", username=username, 
                       riddles_data=data, rIndex=rIndex, wrongAnswersText=wrongAnswersText, 
                       score=score, tries=tries)
            if tries == 0:                                      # if there is no more tries left
                if rIndex == len(data)-1:                       # check if last riddle
                    file_name = "data/" + username + ".txt"
                    saveToFile(file_name, "-------------------------------------------\nScore: " + str(score) + "\n-------------------------------------------")
                    highscoreUpdate(score, username)
                    return render_template("end.html", 
                           username=username, score=score, player=player)
                if rIndex < len(data):                          # if not last riddle
                    rIndex += 1
                    tries = 1
                    return render_template("riddle.html", username=username, 
                           riddles_data=data, rIndex=rIndex, 
                           wrongAnswersText=wrongAnswersText, score=score, 
                           tries=tries)
    return render_template("riddle.html", username=username, 
           riddles_data=data, rIndex=rIndex, wrongAnswersText=wrongAnswersText, score=score, tries=tries)

@app.route('/<username>/endgame', methods=["GET", "POST"])    
def end(username, score):
    return render_template("end.html", 
           username=username, score=score, player=player)
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)