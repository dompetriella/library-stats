import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect
import gunicorn


app = Flask(__name__)

user = {'current_user':''}

#creates a database called stats_database.db
def create_database():
    #connects to file
    conn = sqlite3.connect('stats_database.db')
    #creates cursor to write
    cur = conn.cursor()
    try:
        #creates table 'stats_table'
        #columns id, date_created, time_created, name, t_type
        #sets the primary key to id (used to get info)
        create_table = """
        CREATE TABLE stats_table (
            id INTEGER, 
            date_created VARCHAR,
            time_created VARCHAR,
            name VARCHAR DEFAULT "lib_staff",
            t_type VARCHAR DEFAULT "Reference",
            PRIMARY KEY (id));
        """
        #makes it happen
        cur.executescript(create_table)
        print("created table")
    except:
        print("table already made")
create_database()

#gets date and time for db entries
def get_date_time():
    now = datetime.now()
    _date = now.strftime("%m/%d/%Y")
    _time = now.strftime("%H:%M:%S")
    return {'date':_date, 'time':_time}

def print_database():
    conn = sqlite3.connect('stats_database.db')
    cur = conn.cursor()
    #gets table's items descending eg. 10 -> 1 vs 1 -> 10
    cur.execute("SELECT * FROM stats_table ORDER BY id DESC LIMIT 1")
    #gets the first item, which is the last entry in this case
    data = cur.fetchone()
    print(data)


def write_to_db(entry):
    try:
        conn = sqlite3.connect('stats_database.db')
        cur = conn.cursor()
        date_time = get_date_time()
        #writes to stats_table
        cur.execute('INSERT INTO stats_table (date_created, time_created, name, t_type) VALUES (?, ?, ?, ?)',
                    (date_time['date'], date_time['time'], user['current_user'], entry))
        conn.commit()
    except:
        print("Error: could not write to database")
    print_database()
    conn.close()


@app.route('/')
def home_page():
  return render_template("stats_page.html")

# I WILL MAKE YOU A FLASK FORM AT SOME POINT
@app.route('/login', methods=["POST","GET"])
def login():
    if request.method == "POST":
        login_name = request.form['login_name']
        print(login_name)
        user['current_user'] = login_name
        print(user)
        return redirect('/')

@app.route('/button_press', methods=["POST","GET"])
def button_press():
        if request.method == 'POST':
            if request.form.get('ref_trans') == 'ref_trans':
                write_to_db("Reference Transaction")
            elif request.form.get('ref_redir') == 'ref_redir':
                write_to_db("Reference Transaction Redirected")
            elif request.form.get('phone_call') == 'phone_call':
                write_to_db("Phone Call")
            elif request.form.get('ref_nc') == 'ref_nc':
                write_to_db("Reference Transaction Not Completed")
            else:
                return redirect("/")
        elif request.method == 'GET':
            print("No Post Back Call")
        return redirect("/")


@app.route('/stats_daily')
def daily_stats():
    date_time = get_date_time()
    check_date = date_time['date']
    conn = sqlite3.connect('stats_database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM stats_table WHERE date_created = ?", (check_date,))
    data_found = cur.fetchall()
    daily_dicts = []
    action_totals = {"Reference Transaction":0, "Reference Transaction Redirected":0, "Phone Call":0, "Reference Transaction Not Completed": 0}
    for tdata in data_found:
        entry = {'date':tdata[1],'time':tdata[2],'name':tdata[3],'action':tdata[4]}
        daily_dicts.append(entry)
        for keys in action_totals.keys():
            if tdata[4] == keys:
                action_totals[keys]+=1

    return render_template("stats_daily.html", daily_dicts = daily_dicts, action_totals = action_totals, check_date = check_date)

#for running in pycharm
if __name__ == '__main__':
    app.run()