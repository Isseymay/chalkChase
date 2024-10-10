from flask import Flask, redirect, render_template, request, session 
from flask_session import Session 
import sqlite3

app = Flask(__name__)
app.secret_key = 'encryptionKey'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

leftQs = ["Which side of the road do people in Japan drive on?",
          "Which ear did Vincent Van Gough cut off?",
          "On the Welsh flag, Y Ddraig Goch (the dragon) faces which side?",
          "From which ventricle does the aorta exit the human heart",
          "With which foot did Neil Armstrong first step on the moon?",
          "Which side of a plane will you always board on?",
          "In Peter Pan, on which hand is Captain Hook's hook?",
          "In chess the white queen is set up to which side of the king?"]

rightQs = ["In what hand does the Statue of Liberty hold the torch?",
           "Which direction do you step in the Time Warp?",
           "If you are facing the bow, which side of a boat is 'Starboard'?",
           "On which side of a standard dartboard is the number 13",
           "In a traditional Christian wedding, on which side does the grooms family sit on ?(if you're facing the altar)",
           "Which side of the brain is know as the 'Creative' side?",
           "In what hand does Michelangelo's David hold a rock?",
           "Which hand is the latin origin for the word dexterous?"]

def setup():
  
  conn = sqlite3.connect("data.db")
  msg = "Opened database successfully"
  cur = conn.cursor()

  cur.execute("DROP TABLE if exists users;")
  cur.execute("DROP TABLE if exists questions;")
  print("here")
  cur.execute("CREATE TABLE users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, teamname, currentQ INTEGER, FOREIGN KEY (currentQ) REFERENCES questions(question_id))")
  print("here 2")
  cur.execute("CREATE TABLE questions(question_id INTEGER PRIMARY KEY AUTOINCREMENT, question, ans, street)")
  print("here 3")
  cur.execute("INSERT INTO questions (question,street) VALUES (?,?)",("No question yet",""))
  cur.execute("INSERT INTO users (teamname,currentQ) VALUES (?,?)",("1",0))
  msg += "Tables created successfully"
  conn.commit()
  print("here 4")
  conn.close()
  print(msg)
  return msg



@app.before_request
def before_request():
  
  session.permanent = True
  

@app.route("/", methods=["GET","POST"])
def guest():
  if 'user' in session:
    user_id = session['user']
    print(user_id)

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("SELECT teamname AS name,questions.question AS q from users inner join questions on users.currentQ = questions.question_id where user_id = ?",(user_id,))
    team = cur.fetchall()
    print(team,"  ......")
    if team!=[]:
      name = team[0][0]
      question = team[0][1]

      if request.method=="POST":
        query = request.form['street']

        cur.execute("SELECT question,street from questions where question_id = ((SELECT question_id from questions where question = ?)+1)",(question,))
        next = cur.fetchall()

        if next[0][1]==query:
          question = next[0][0]

      return render_template("guest.html",team=name,current=question)
    else:
      return redirect("/login")
  else:
    return redirect("/login")
  
@app.route("/login", methods=["GET","POST"])
def login():
  if request.method == "GET":
    session.clear()
    return render_template('login.html')
  else:
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    teamname = request.form["teamname"]

    cur.execute("SELECT user_id from users WHERE teamname = ?",(teamname,))
    user = cur.fetchall()
    print(user)
    if user !=[]:
        session['user'] = user[0][0]
        print(teamname)
        if teamname == "1":
            return redirect("/admin")
        else:
            return redirect("/")
    else:
        cur.execute("INSERT INTO users(teamname, currentQ) VALUES(?,?)",(teamname, 1))
        conn.commit()
        conn.close()

        conn = sqlite3.connect("data.db")
        cur = conn.cursor()

        cur.execute("SELECT user_id from users WHERE teamname = ?",(teamname,))
        user = cur.fetchall()

        cur.execute("SELECT * from users")
        all=cur.fetchall()
        print(all)
        print("here",user[0][0])
        session['user'] = user[0][0]
        return redirect("/")

@app.route("/admin", methods=["GET","POST"])
def admin():
    
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    
    cur.execute("SELECT teamname as team,users.currentQ as current, street from users inner join questions on users.currentQ = questions.question_id order by currentQ")
    teams = cur.fetchall()

    msg=""

    if request.method == "POST":
        ans = request.form["dir"]
        street = request.form["street"]

        cur.execute("SELECT COUNT() as count from questions where ans = ?",(ans,))
        count=cur.fetchall()

        msg=""
        print(count)
        if count[0][0]>7:
            msg=f"No more questions for {ans}"
            return render_template("admin.html",msg=msg, teams=teams)
        else:
            if ans == "left":
                question = leftQs[count[0][0]]
            else:
                question = rightQs[count[0][0]]

            cur.execute("INSERT INTO questions (question, ans, street) VALUES(?,?,?)",(question,ans,street))
            conn.commit()
            msg="Question successfully added"
            return render_template("admin.html",msg=msg, teams=teams)
    else:
      return render_template("admin.html", msg=msg, teams=teams)




app.run(host='0.0.0.0', port=81, debug=True)
