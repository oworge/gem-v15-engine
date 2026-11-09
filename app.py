from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    tab = request.args.get('tab', 'dailypicks')
    dailypicks = [{'home': 'Arsenal', 'away': 'Chelsea', 'market': 'Home Win', 'odds': '1.85'}]
    btts_slate = [{'home': 'Real Madrid', 'away': 'Barcelona', 'market': 'BTTS - Yes', 'odds': '1.70'}]
    acca_slate = [{'home': 'Dortmund', 'away': 'Bayern', 'market': 'Over 2.5', 'odds': '1.90'}]
    return render_template('index.html', active_tab=tab, dailypicks=dailypicks, btts_slate=btts_slate, acca_slate=acca_slate)

if __name__ == '__main__':
    app.run(port=5000)
