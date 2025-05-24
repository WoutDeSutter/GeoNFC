from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .database import Database
import os

app = Flask(__name__, static_folder='../static')
CORS(app)
db = Database()

# API Routes
@app.route('/api/caches')
def get_caches():
    tags = db.get_all_tags()
    return jsonify([{
        'tag_id': tag[0],
        'latitude': tag[1],
        'longitude': tag[2],
        'last_updated': tag[3].isoformat() if tag[3] else None
    } for tag in tags])

@app.route('/api/tag/<tag_id>')
def get_tag(tag_id):
    print(f"\nAPI: Zoeken naar tag {tag_id}")
    try:
        tag = db.get_tag(tag_id)
        if not tag:
            print(f"API: Tag {tag_id} niet gevonden")
            return jsonify({'error': f'Tag {tag_id} not found'}), 404
        print(f"API: Tag gevonden: {tag}")
        return jsonify({
            'tag_id': tag[0],
            'latitude': tag[1],
            'longitude': tag[2],
            'last_updated': tag[3].isoformat() if tag[3] else None
        })
    except Exception as e:
        print(f"API Error bij ophalen tag: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/log', methods=['POST'])
def create_log():
    data = request.json
    tag_id = data.get('tag_id')
    username = data.get('username')
    message = data.get('message')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not all([tag_id, username, message, latitude, longitude]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if tag exists
    tag = db.get_tag(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    # Add log and update tag location
    db.add_log(tag_id, username, message, latitude, longitude)
    db.update_tag_location(tag_id, latitude, longitude)
    
    return jsonify({'success': True})

@app.route('/api/logs/<tag_id>')
def get_logs(tag_id):
    logs = db.get_tag_logs(tag_id)
    return jsonify([{
        'username': log[0],
        'message': log[1],
        'latitude': log[2],
        'longitude': log[3],
        'timestamp': log[4].isoformat() if log[4] else None
    } for log in logs])

@app.route('/api/all-logs')
def get_all_logs():
    logs = db.get_all_logs()
    return jsonify([{
        'tag_id': log[0],
        'username': log[1],
        'message': log[2],
        'latitude': log[3],
        'longitude': log[4],
        'timestamp': log[5].isoformat() if log[5] else None
    } for log in logs])

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