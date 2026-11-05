from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head><title>EDGEMETRIX V300</title></head>
<body style="background:#0b0f19;color:white;font-family:sans-serif;padding:40px;text-align:center;">
    <h1>EDGEMETRIX V300 DASHBOARD</h1>
    <p style="color:#4ade80;font-size:18px;">Status: ONLINE (Flask & Gunicorn Active)</p>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

