print("JARVIS backend starting...")

from flask import Flask, request, jsonify, render_template
import webbrowser
import os
import threading
import time
import subprocess
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# ---------------- FILES ----------------
LOGIN_FILE = "login_logs.xlsx"
COMMAND_FILE = "command_logs.xlsx"


# ---------------- INIT EXCEL FILES ----------------
def init_files():
    if not os.path.exists(LOGIN_FILE):
        pd.DataFrame(columns=["time", "status"]).to_excel(LOGIN_FILE, index=False)

    if not os.path.exists(COMMAND_FILE):
        pd.DataFrame(columns=["time", "command", "response"]).to_excel(COMMAND_FILE, index=False)

init_files()


# ---------------- LOG FUNCTIONS ----------------
def log_login(status):
    df = pd.read_excel(LOGIN_FILE)
    df.loc[len(df)] = [datetime.now(), status]
    df.to_excel(LOGIN_FILE, index=False)


def log_command(command, response):
    df = pd.read_excel(COMMAND_FILE)
    df.loc[len(df)] = [datetime.now(), command, response]
    df.to_excel(COMMAND_FILE, index=False)


# ---------------- DESKTOP COMMANDS ----------------
def desktop_control(command):

    cmd = command.lower()

    if "youtube" in cmd:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"

    if "google" in cmd:
        webbrowser.open("https://google.com")
        return "Opening Google"

    if "calculator" in cmd:
        os.system("calc")
        return "Opening Calculator"

    if "notepad" in cmd:
        os.system("notepad")
        return "Opening Notepad"

    if "time" in cmd:
        return f"Current time: {datetime.now().strftime('%H:%M:%S')}"

    if "date" in cmd:
        return f"Today's date: {datetime.now().strftime('%Y-%m-%d')}"

    return None


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("jarvis2.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    try:
        login_data = pd.read_excel(LOGIN_FILE).fillna("")
        command_data = pd.read_excel(COMMAND_FILE).fillna("")
    except:
        login_data = pd.DataFrame(columns=["time", "status"])
        command_data = pd.DataFrame(columns=["time", "command", "response"])

    return render_template(
        "dashboard.html",
        login_tables=login_data.to_dict(orient="records"),
        command_tables=command_data.to_dict(orient="records")
    )


# ---------------- LOGIN (NO PASSWORD SYSTEM) ----------------
@app.route("/voice_login", methods=["POST"])
def voice_login():

    log_login("LOGIN ATTEMPT")
    return jsonify({"access": True})


# ---------------- PROCESS COMMAND ----------------
@app.route("/process", methods=["POST"])
def process():

    command = request.json["command"]

    response = desktop_control(command)

    if response is None:
        response = "Command not recognized"

    log_command(command, response)

    return jsonify({"response": response})


# ---------------- AUTO OPEN CHROME ----------------
def open_browser():
    time.sleep(1)

    try:
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        subprocess.run([chrome_path, "http://localhost:5000"])
    except:
        webbrowser.open("http://localhost:5000")


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="0.0.0.0", port=5000, debug=True)