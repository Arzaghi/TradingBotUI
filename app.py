from flask import Flask, render_template, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

DATA_DIR = "/HDD"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/current_positions')
def api_current_positions():
    df = pd.read_csv(os.path.join(DATA_DIR, 'current_positions.csv'))
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/positions_history')
def api_positions_history():
    df = pd.read_csv(os.path.join(DATA_DIR, 'positions_history.csv'))
    return jsonify(df.to_dict(orient='records'))

@app.route('/download/history')
def download_history():
    return send_file(os.path.join(DATA_DIR, 'positions_history.csv'), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
