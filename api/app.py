from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .database import Database
from .scheduler import init_scheduler
import os

print("Flask application starting...")

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
init_scheduler()

# API Routes
@app.route('/api/caches', methods=['GET'])
def get_caches():
    print("Fetching all caches...")
    # Add pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # You would ideally pass these to your db.get_all_tags() method
    # caches = db.get_all_tags(page=page, per_page=per_page)
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
    # Add pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # You would ideally pass these to your db.get_logs() method
    # logs = db.get_logs(tag_id, page=page, per_page=per_page)
    logs = db.get_logs(tag_id)
    print(f"Found {len(logs)} logs: {logs}")
    return jsonify(logs)

@app.route('/api/all-logs', methods=['GET'])
def get_all_logs():
    print("Fetching all logs...")
    # Add pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # You would ideally pass these to your db.get_all_logs() method
    # logs = db.get_all_logs(page=page, per_page=per_page)
    logs = db.get_all_logs()
    print(f"Found {len(logs)} logs: {logs}")
    return jsonify(logs)

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
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 