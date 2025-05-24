from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .database import Database
# from .scheduler import init_scheduler
import os

app = Flask(__name__, static_folder='../static')
CORS(app)

# Initialiseer de database
try:
    db = Database()
    print("Database initialized successfully in app.py")
except Exception as e:
    print(f"Error initializing database in app.py: {e}")
    # Optionally, re-raise the exception if you want the deployment to fail explicitly
    # raise

# Initialiseer de scheduler
# init_scheduler()

# API Routes
@app.route('/api/caches', methods=['GET'])
def get_caches():
    print("Fetching all caches...")
    caches = db.get_all_tags()
    print(f"Found {len(caches)} caches: {caches}")
    return jsonify(caches)

@app.route('/api/tag/<tag_id>', methods=['GET'])
def get_tag(tag_id):
    print(f"\nAPI: Zoeken naar tag {tag_id}")
    try:
        tag = db.get_tag(tag_id)
        if not tag:
            print(f"API: Tag {tag_id} niet gevonden")
            return jsonify({'error': f'Tag {tag_id} not found'}), 404
        print(f"API: Tag gevonden: {tag}")
        return jsonify(tag)
    except Exception as e:
        print(f"API Error bij ophalen tag: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/log', methods=['POST'])
def add_log():
    data = request.json
    print(f"Received log data: {data}")
    if not all(k in data for k in ['tag_id', 'username', 'message', 'latitude', 'longitude']):
        print("Missing required fields in log data")
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = db.add_log(
        data['tag_id'],
        data['username'],
        data['message'],
        data['latitude'],
        data['longitude']
    )
    
    if success:
        print("Log successfully added")
        return jsonify({'message': 'Log added successfully'})
    print("Failed to add log")
    return jsonify({'error': 'Failed to add log'}), 500

@app.route('/api/logs/<tag_id>', methods=['GET'])
def get_logs(tag_id):
    print(f"Fetching logs for tag {tag_id}")
    logs = db.get_logs(tag_id)
    print(f"Found {len(logs)} logs: {logs}")
    return jsonify(logs)

@app.route('/api/all-logs', methods=['GET'])
def get_all_logs():
    print("Fetching all logs...")
    logs = db.get_all_logs()
    print(f"Found {len(logs)} logs: {logs}")
    return jsonify(logs)

@app.route('/api/create_test_tag')
def create_test_tag():
    """Maak een test tag aan voor development"""
    try:
        print("Test tag aanmaken...")
        
        # Eerst controleren of de tag al bestaat
        existing_tag = db.get_tag('TEST001')
        if existing_tag:
            print(f"Tag TEST001 bestaat al: {existing_tag}")
            return jsonify({
                'success': True, 
                'message': 'Test tag TEST001 already exists', 
                'tag': existing_tag
            })

        # Tag aanmaken als deze nog niet bestaat
        print("Proberen test tag aan te maken...")
        success = db.add_tag('TEST001', 'Test Cache', 50.8503, 4.3517)  # Brussel coördinaten
        if not success:
            print("Kon test tag niet aanmaken")
            return jsonify({
                'error': 'Failed to create test tag',
                'details': 'Database operation failed'
            }), 500

        print("Test tag aangemaakt, controleren of deze bestaat...")
        tag = db.get_tag('TEST001')
        print(f"Tag controle resultaat: {tag}")
        
        if not tag:
            print("Tag niet gevonden na aanmaken!")
            return jsonify({
                'error': 'Tag not found after creation',
                'details': 'Tag was created but could not be retrieved'
            }), 500

        return jsonify({
            'success': True, 
            'message': 'Test tag TEST001 created', 
            'tag': tag
        })
    except Exception as e:
        print(f"Error bij aanmaken test tag: {str(e)}")
        return jsonify({
            'error': str(e),
            'details': 'An unexpected error occurred'
        }), 500

@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

@app.route('/add_log/<tag_id>')
def add_log_page(tag_id):
    return send_from_directory('..', 'add_log.html')

@app.route('/logs')
def logs_page():
    return send_from_directory('..', 'logs.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 