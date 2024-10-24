from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from service_analyzer import analyze_chat_for_services, analyze_chat_text
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Configuration for Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/openapi.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Service Analyzer API'
    }
)

# Register Swagger UI blueprint
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    return render_template('home.html')  # Render the home template

@app.route('/analyze-text')
def analyze_text_page():
    return render_template('analyze_text.html')  # Render the analyze text page

# Serve the OpenAPI specification
@app.route(API_URL)
def openapi_spec():
    return send_from_directory('static', 'openapi.json', mimetype='application/json')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = 'temp_chat_file.txt'
    file.save(file_path)

    # Analyze the chat
    result = analyze_chat_for_services(file_path)

    # Remove the temporary file
    os.remove(file_path)

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to analyze chat"}), 500
    
@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No 'text' field in request"}), 400

    chat_text = data['text']
    result = analyze_chat_text(chat_text)

    return jsonify(result) 

if __name__ == '__main__':
    # Get the port from the environment variable PORT or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
