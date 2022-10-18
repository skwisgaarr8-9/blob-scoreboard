import sqlite3
from flask import Flask, render_template, request



app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True



@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
    

@app.route("/homepage", methods=["GET", "POST"])
def homepage():
    return render_template("homepage.html")

@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():

    if request.method == "POST":
        # empty dict for players
        players_dict = {}
        #get list of players from scoreboard
        players = request.form.getlist("player")
        # get list of bets from scoreboard
        bets = request.form.getlist("bets")
        # get list of blobs from scoreboard
        blobs = request.form.getlist("blobs")
        
        # create nested dict in players_dict for each player
        # add each player's name
        i = 0
        for player in players:
            player.strip()
            players_dict['player' + str(i + 1)] = {"name": player, "blobs": 0, "bets": 0}
            i += 1
        # update each player's total bets
        i = 0
        for bet in bets:
            players_dict['player' + str(i + 1)]["bets"] = bet
            i += 1
        # update each player's total blobs
        i = 0
        for blob in blobs:
            players_dict['player' + str(i + 1)]["blobs"] = blob
            i += 1
        
        # set variable for winner, most bets, and least blobs
        winner = players_dict["player1"]["name"]
        most_bets = players_dict["player1"]["bets"]    
        least_blobs = players_dict["player1"]["blobs"]
    
        # iterate through current players, comparing blobs
        # if player has lowest blobs, set name to winner
        # if blobs are equal, check bets. set most bets name to winner
        for player in players_dict:
            if players_dict[player]["blobs"] < least_blobs:
                least_blobs = players_dict[player]["blobs"]
                winner = players_dict[player]["name"]
                most_bets = players_dict[player]["bets"]
            elif players_dict[player]["blobs"] == least_blobs:
                if players_dict[player]["bets"] > most_bets:
                    most_bets = players_dict[player]["bets"]
                    winner = players_dict[player]["name"]

        # update players.db players table with played game's stats
        conn = sqlite3.connect('players.db')
        db = conn.cursor()

        #iterate through players_dict and update each player's stats in players.db
        for player in players_dict:
            db.execute("UPDATE players SET blobs = blobs + ? WHERE name LIKE ?", (players_dict[player]["blobs"], players_dict[player]["name"]))
            if players_dict[player]["name"] == winner:
                db.execute("UPDATE players SET wins = wins + 1 WHERE name LIKE ?", (winner,))

        #get updated info from players.db
        #sort by wins, descending
        #show leaderboard
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        db.execute("SELECT * FROM players WHERE blobs > 0")
        leaderboard = db.fetchall()
        leaderboard = sorted(leaderboard, key = lambda x: x["wins"], reverse=True)
        conn.commit()
        conn.close()

        return render_template("leaderboard.html", players=leaderboard)

    #if method = get, get information from players.db and list by wins
    else:
        conn = sqlite3.connect('players.db')
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        db.execute("SELECT * FROM players WHERE blobs > 0")
        leaderboard = db.fetchall()
        #sort data from players.db by wins, descending
        leaderboard = sorted(leaderboard, key = lambda x: x["wins"], reverse=True)
        conn.commit()
        conn.close()

        return render_template("leaderboard.html", players=leaderboard)

@app.route("/scoreboard", methods=["GET", "POST"])
def scoreboard():


    if request.method == "POST":
        conn = sqlite3.connect('players.db')
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, name TEXT NOT NULL, wins NUMERIC NOT NULL DEFAULT 0, blobs NUMERIC NOT NULL DEFAULT 0)")
        db.execute("SELECT name FROM players")
        current_players = request.form.getlist("player")
        returning_players = []

        # fill returning_players list with names from players.db
        for player in db.fetchall():
            person = player[0]
            returning_players.append(person.lower())

        #if players.db is empty, insert the players into the db
        if len(returning_players) == 0:
            for player in current_players:
                player.strip()
                db.execute("INSERT INTO players (name) VALUES (?)", (player,))
                conn.commit()
        else:
            #check if each current player is in players.db
            for player in current_players:
                #if player is in players.db, skip
                if returning_players.count(player.lower().strip()) > 0:
                    continue
                #else, add the new player to players.db
                else:
                    player.strip()
                    db.execute("INSERT INTO players (name) VALUES (?)", (player,))
                    conn.commit()
        

        
        return render_template("scoreboard.html", players=current_players)        

