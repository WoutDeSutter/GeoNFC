import mysql.connector
import os
from datetime import datetime, timedelta
from .config import Config

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self.initialize_database()

    def initialize_database(self):
        # Create tables if they don't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tag_id VARCHAR(50) NOT NULL,
                username VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()

    def cleanup_inactive_caches(self, days_inactive=365):
        """
        Verwijderd caches en hun logs die langer dan 'days_inactive' dagen niet zijn gelogd.
        """
        try:
            # Bereken de cutoff datum
            cutoff_date = datetime.now() - timedelta(days=days_inactive)
            
            # Vind alle caches die geen logs hebben na de cutoff datum
            self.cursor.execute("""
                SELECT t.id 
                FROM tags t 
                LEFT JOIN logs l ON t.id = l.tag_id 
                GROUP BY t.id 
                HAVING MAX(l.timestamp) < %s OR MAX(l.timestamp) IS NULL
            """, (cutoff_date,))
            
            inactive_caches = self.cursor.fetchall()
            
            if not inactive_caches:
                return 0
            
            # Verwijder de inactieve caches (logs worden automatisch verwijderd door ON DELETE CASCADE)
            cache_ids = [cache['id'] for cache in inactive_caches]
            placeholders = ', '.join(['%s'] * len(cache_ids))
            
            self.cursor.execute(f"""
                DELETE FROM tags 
                WHERE id IN ({placeholders})
            """, tuple(cache_ids))
            
            self.conn.commit()
            return len(cache_ids)
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error cleaning up inactive caches: {str(e)}")
            return 0

    def add_tag(self, tag_id, name, latitude, longitude):
        try:
            self.cursor.execute(
                "INSERT INTO tags (id, name, latitude, longitude) VALUES (%s, %s, %s, %s)",
                (tag_id, name, latitude, longitude)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding tag: {str(e)}")
            return False

    def get_tag(self, tag_id):
        try:
            self.cursor.execute("SELECT * FROM tags WHERE id = %s", (tag_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting tag: {str(e)}")
            return None

    def get_all_tags(self):
        try:
            self.cursor.execute("SELECT * FROM tags")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all tags: {str(e)}")
            return []

    def add_log(self, tag_id, username, message, latitude, longitude):
        try:
            self.cursor.execute(
                "INSERT INTO logs (tag_id, username, message, latitude, longitude) VALUES (%s, %s, %s, %s, %s)",
                (tag_id, username, message, latitude, longitude)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding log: {str(e)}")
            return False

    def get_logs(self, tag_id):
        try:
            self.cursor.execute("SELECT * FROM logs WHERE tag_id = %s ORDER BY timestamp DESC", (tag_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting logs: {str(e)}")
            return []

    def get_all_logs(self):
        try:
            self.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all logs: {str(e)}")
            return []

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close() 