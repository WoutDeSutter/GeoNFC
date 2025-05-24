from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .database import Database
from .scheduler import init_scheduler
import os

app = Flask(__name__, static_folder='../static')
CORS(app)

# Initialiseer de database
db = Database()

# Initialiseer de scheduler
init_scheduler()

# API Routes
@app.route('/api/caches', methods=['GET'])
def get_caches():
    caches = db.get_all_tags()
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
    if not all(k in data for k in ['tag_id', 'username', 'message', 'latitude', 'longitude']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = db.add_log(
        data['tag_id'],
        data['username'],
        data['message'],
        data['latitude'],
        data['longitude']
    )
    
    if success:
        return jsonify({'message': 'Log added successfully'})
    return jsonify({'error': 'Failed to add log'}), 500

@app.route('/api/logs/<tag_id>', methods=['GET'])
def get_logs(tag_id):
    logs = db.get_logs(tag_id)
    return jsonify(logs)

@app.route('/api/all-logs', methods=['GET'])
def get_all_logs():
    logs = db.get_all_logs()
    return jsonify(logs)

@app.route('/api/create_test_tag')
def create_test_tag():
    """Maak een test tag aan voor development"""
    try:
        print("Test tag aanmaken...")
        db.add_tag('TEST001', 50.8503, 4.3517)  # Brussel coördinaten
        print("Test tag aangemaakt, controleren of deze bestaat...")
        tag = db.get_tag('TEST001')
        print(f"Tag controle resultaat: {tag}")
        return jsonify({'success': True, 'message': 'Test tag TEST001 created', 'tag': tag})
    except Exception as e:
        print(f"Error bij aanmaken test tag: {str(e)}")
        return jsonify({'error': str(e)}), 500

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