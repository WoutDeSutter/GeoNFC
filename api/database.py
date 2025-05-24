import mysql.connector
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',  # Pas dit aan naar je MySQL gebruikersnaam
            'password': 'root',  # Pas dit aan naar je MySQL wachtwoord
            'database': 'geonfc'  # Aangepaste database naam
        }
        try:
            self.init_db()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            raise

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            raise

    def init_db(self):
        """Initialize the database if it doesn't exist"""
        try:
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()

            # Maak database aan als deze niet bestaat
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Database initialization error: {err}")
            raise

    def add_tag(self, tag_id, latitude, longitude):
        """Add or update a tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            print(f"Toevoegen tag: {tag_id} op locatie {latitude}, {longitude}")
            cursor.execute("""
                INSERT INTO tags (tag_id, latitude, longitude, last_updated)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    latitude = VALUES(latitude),
                    longitude = VALUES(longitude),
                    last_updated = VALUES(last_updated)
            """, (tag_id, latitude, longitude, datetime.utcnow()))
            conn.commit()
            print(f"Tag {tag_id} succesvol toegevoegd/geüpdatet")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error adding tag: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def add_log(self, tag_id, username, message, latitude, longitude):
        """Add a new log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO logs (tag_id, username, message, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
            """, (tag_id, username, message, latitude, longitude))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error adding log: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_all_tags(self):
        """Get all tags with their latest location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT tag_id, latitude, longitude, last_updated
                FROM tags
                ORDER BY last_updated DESC
            """)
            results = cursor.fetchall()
            print(f"Alle tags in database: {results}")  # Debug logging
            return results
        except mysql.connector.Error as err:
            print(f"Error getting tags: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_tag_logs(self, tag_id):
        """Get all logs for a specific tag"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT username, message, latitude, longitude, timestamp
                FROM logs
                WHERE tag_id = %s
                ORDER BY timestamp DESC
            """, (tag_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting tag logs: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_all_logs(self):
        """Get all logs from all tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT l.tag_id, l.username, l.message, l.latitude, l.longitude, l.timestamp
                FROM logs l
                ORDER BY l.timestamp DESC
            """)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting all logs: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_tag(self, tag_id):
        """Haal een specifieke tag op."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            print(f"Database verbinding gemaakt voor tag: {tag_id}")
            
            # Eerst kijken welke tags er allemaal in de database staan
            cursor.execute("SELECT tag_id FROM tags")
            all_tags = cursor.fetchall()
            print(f"Alle tags in database: {all_tags}")
            
            # Nu de specifieke tag ophalen
            query = 'SELECT * FROM tags WHERE tag_id = %s'
            print(f"Uitvoeren query: {query} met tag_id={tag_id}")
            cursor.execute(query, (tag_id,))
            result = cursor.fetchone()
            print(f"Query resultaat: {result}")
            
            return result
        except mysql.connector.Error as err:
            print(f"Database error bij ophalen tag: {err}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_tag_location(self, tag_id, latitude, longitude):
        """Update de locatie van een bestaande tag."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tags 
                SET latitude = %s, longitude = %s, last_updated = NOW()
                WHERE tag_id = %s
            ''', (latitude, longitude, tag_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close() 