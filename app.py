from flask import Flask, render_template, jsonify, send_file
import pandas as pd
import os
from pandas.errors import EmptyDataError # Import specific error

app = Flask(__name__)

# Assuming DATA_DIR contains the path to the CSV files
DATA_DIR = "/HDD"

# Helper function to ensure the 'profit' column is safe for calculation
def load_and_clean_history_df(filepath):
    df = pd.read_csv(filepath)
    # FIX: Strip whitespace from column names to prevent KeyError if the CSV has spaces in headers
    df.columns = df.columns.str.strip()
    # Convert 'profit' to numeric, coercing errors to NaN and filling with 0
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/current_positions')
def api_current_positions():
    df = pd.read_csv(os.path.join(DATA_DIR, 'current_positions.csv'))
    # FIX: Strip column names here too, for robustness
    df.columns = df.columns.str.strip()
    return jsonify(df.to_dict(orient='records'))

# Define a default stats dictionary for error cases
DEFAULT_STATS = {
    'total_records': 0,
    'long_count': 0,
    'short_count': 0,
    'total_profit': 0, # Changed to int
    'zero_profit_count': 0,
    'negative_profit_count': 0,
    'positive_profit_sum': 0, # Changed to int
    'winning_trades_count': 0 # New default stat
}

@app.route('/api/positions_history')
def api_positions_history():
    # Attempting to return empty list on error for consistency with loadHistory JS function
    filepath = os.path.join(DATA_DIR, 'positions_history.csv')
    try:
        df = pd.read_csv(filepath)
        # FIX: Strip column names for consistency
        df.columns = df.columns.str.strip()
        return jsonify(df.to_dict(orient='records'))
    except (FileNotFoundError, EmptyDataError):
        # Return an empty list if file is missing or empty
        return jsonify([])
    except Exception as e:
        print(f"Error loading positions history: {e}")
        return jsonify({"error": "Failed to load history data"}), 500

@app.route('/api/history_stats')
def api_history_stats():
    """Calculates and returns key statistics from the positions history."""
    filepath = os.path.join(DATA_DIR, 'positions_history.csv')
    try:
        df = load_and_clean_history_df(filepath)
        
        # All counts and sums are converted to Python standard types (int/float)
        # to ensure they are JSON serializable.
        total_records = len(df)
        long_count = df[df['type'] == 'Long'].shape[0]
        short_count = df[df['type'] == 'Short'].shape[0]
        total_profit = df['profit'].sum()
        zero_profit_count = df[df['profit'] == 0].shape[0]
        negative_profit_count = df[df['profit'] < 0].shape[0]
        positive_profit_sum = df[df['profit'] > 0]['profit'].sum()
        winning_trades_count = df[df['profit'] > 0].shape[0] 

        # Applying user request: Format R-multiples as integers by rounding and casting to int.
        # NOTE: Dollar-based profit (calculated in JS) remains float for accuracy, but R-multiples are now int.
        stats = {
            'total_records': int(total_records),
            'long_count': int(long_count),
            'short_count': int(short_count),
            'total_profit': int(round(float(total_profit))), # Total R-multiple SUM, formatted as INT
            'zero_profit_count': int(zero_profit_count),
            'negative_profit_count': int(negative_profit_count),
            'positive_profit_sum': int(round(float(positive_profit_sum))), # Positive R-multiple SUM, formatted as INT
            'winning_trades_count': int(winning_trades_count)
        }
        
        return jsonify(stats)
    except (FileNotFoundError, EmptyDataError):
        # Return default zero stats if file is missing or empty
        return jsonify(DEFAULT_STATS)
    except Exception as e:
        # Catch other errors (like permissions)
        print(f"Error processing history stats: {e}")
        # Return a generic 500 error response
        return jsonify({"error": "Failed to calculate statistics"}), 500

@app.route('/download/history')
def download_history():
    """Downloads the position history CSV file."""
    # Note: Use as_attachment=True for actual download
    return send_file(os.path.join(DATA_DIR, 'positions_history.csv'), as_attachment=True)

if __name__ == '__main__':
    # Changed port to match the one in the JavaScript
    app.run(host='0.0.0.0', port=5000)