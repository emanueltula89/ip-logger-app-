import os
from flask import Flask, request
import gspread
from datetime import datetime

# --- Configuration ---
# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = 'ip-scan-476101-fcfb7c4ada39.json'
# The ID of your Google Spreadsheet (from the URL)
SPREADSHEET_ID = '1mmGfBXq2NVxEaAbCziskAU5OwveLsqsnCB5g2NEU0nY'
# The name of the worksheet within the spreadsheet (e.g., "Hoja 1")
WORKSHEET_NAME = 'Hoja 1'

app = Flask(__name__)

# --- Google Sheets Setup ---
try:
    # Ensure the service account file exists
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    print(f"Successfully connected to Google Sheet: {SPREADSHEET_ID}, Worksheet: {WORKSHEET_NAME}")
except Exception as e:
    print(f"Error connecting to Google Sheets: {e}")
    # Exit or handle error appropriately if connection fails
    exit(1) # Exit if we can't connect to sheets, as it's a core requirement

@app.route('/')
def index():
    # Get the visitor's IP address
    # X-Forwarded-For is used when behind a proxy/load balancer
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"Received connection from IP: {visitor_ip} at {timestamp}")

    try:
        # Append the IP and timestamp to the Google Sheet
        worksheet.append_row([timestamp, visitor_ip])
        print("IP logged successfully to Google Sheet.")
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>¡Gracias por tu visita!</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f0f0; color: #333; }}
                .container {{ text-align: center; padding: 30px; border-radius: 10px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                h1 {{ color: #4CAF50; }}
                p {{ font-size: 1.1em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>¡Hola!</h1>
                <p>Tu visita ha sido registrada. ¡Gracias!</p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        print(f"Error writing to Google Sheet: {e}")
        return "Ocurrió un error al registrar tu visita. Por favor, inténtalo de nuevo más tarde.", 500

if __name__ == '__main__':
    # Run the Flask app
    # host='0.0.0.0' makes the server accessible from any IP address, not just localhost
    # debug=True is useful for development, but should be False in production
    app.run(host='0.0.0.0', port=5000, debug=False)