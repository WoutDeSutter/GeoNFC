import mysql.connector
import os
from datetime import datetime, timedelta
from .config import Config
import time

class Database:
    def __init__(self):
        print(f"Connecting to database at {Config.DB_HOST}:{Config.DB_PORT}")
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.connect_with_retry()

    def connect_with_retry(self):
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting database connection (attempt {attempt + 1}/{self.max_retries})")
                print(f"Connection details: host={Config.DB_HOST}, port={Config.DB_PORT}, user={Config.DB_USER}, database={Config.DB_NAME}")
                
                # First connect without database to create it if it doesn't exist
                temp_conn = mysql.connector.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                print("Initial connection successful")
                cursor = temp_conn.cursor()
                
                # Create database if it doesn't exist
                print(f"Creating database {Config.DB_NAME} if it doesn't exist")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
                cursor.close()
                temp_conn.close()
                print("Database creation/verification successful")
                
                # Now connect to the specific database
                print("Connecting to specific database")
                self.conn = mysql.connector.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME
                )
                print("Database connection successful")
                self.cursor = self.conn.cursor(dictionary=True)
                self.initialize_database()
                return
            except mysql.connector.Error as err:
                print(f"MySQL Error during connection attempt {attempt + 1}:")
                print(f"Error Code: {err.errno}")
                print(f"Error Message: {err.msg}")
                print(f"SQL State: {err.sqlstate}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise

    def wait_for_operation(self, operation_name, check_func, max_attempts=3):
        """Wacht tot een database operatie is voltooid"""
        for attempt in range(max_attempts):
            if check_func():
                print(f"{operation_name} completed successfully")
                return True
            print(f"Waiting for {operation_name} to complete... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(self.retry_delay)
        print(f"{operation_name} failed after {max_attempts} attempts")
        return False

    def initialize_database(self):
        print("Initializing database tables...")
        try:
            # Drop existing tables if they exist
            print("Dropping existing tables if they exist...")
            self.cursor.execute("DROP TABLE IF EXISTS logs")
            self.cursor.execute("DROP TABLE IF EXISTS tags")
            
            # Create tags table
            print("Creating tags table...")
            self.cursor.execute("""
                CREATE TABLE tags (
                    tag_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            print("Tags table created")
            
            # Create logs table
            print("Creating logs table...")
            self.cursor.execute("""
                CREATE TABLE logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tag_id VARCHAR(50) NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
                )
            """)
            print("Logs table created")
            
            self.conn.commit()
            print("Database tables initialized successfully")
            
            # Verify tables exist
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            print(f"Existing tables: {tables}")
            
            # Verify table structure
            print("Verifying table structure...")
            self.cursor.execute("DESCRIBE tags")
            tags_structure = self.cursor.fetchall()
            print(f"Tags table structure: {tags_structure}")
            
            self.cursor.execute("DESCRIBE logs")
            logs_structure = self.cursor.fetchall()
            print(f"Logs table structure: {logs_structure}")
            
        except mysql.connector.Error as err:
            print(f"Error initializing database: {err}")
            print(f"Error Code: {err.errno}")
            print(f"Error Message: {err.msg}")
            print(f"SQL State: {err.sqlstate}")
            raise

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
            print(f"Adding tag {tag_id} with name {name} at {latitude}, {longitude}")
            
            # First check if tag exists
            print("Checking if tag already exists using get_tag")
            existing_tag = self.get_tag(tag_id)
            if existing_tag:
                print(f"Tag {tag_id} already exists: {existing_tag}")
                return True
            
            # Add new tag
            print("Inserting new tag")
            query = "INSERT INTO tags (tag_id, name, latitude, longitude) VALUES (%s, %s, %s, %s)"
            params = (tag_id, name, latitude, longitude)
            print(f"Executing query: {query} with params: {params}")
            self.cursor.execute(query, params)
            print("Committing transaction")
            self.conn.commit()
            print("Tag added successfully")
            
            # Verify tag was added
            def verify_tag():
                print("Verifying tag was added using get_tag")
                return self.get_tag(tag_id) is not None

            if self.wait_for_operation("Tag verification", verify_tag):
                print(f"Tag {tag_id} successfully verified.")
                return True
            else:
                print(f"Tag {tag_id} verification failed.")
                return False

        except mysql.connector.Error as err:
            print(f"MySQL Error adding tag:")
            print(f"Error Code: {err.errno}")
            print(f"Error Message: {err.msg}")
            print(f"SQL State: {err.sqlstate}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Unexpected error adding tag: {str(e)}")
            print(f"Error type: {type(e)}")
            self.conn.rollback()
            return False

    def get_tag(self, tag_id):
        try:
            print(f"Executing get_tag query for {tag_id}...")
            
            def get_tag_with_retry():
                query = "SELECT * FROM tags WHERE tag_id = %s"
                print(f"Executing query: {query} with params: ({tag_id},)")
                self.cursor.execute(query, (tag_id,))
                return self.cursor.fetchone()

            # Probeer de tag meerdere keren op te halen
            for attempt in range(self.max_retries):
                result = get_tag_with_retry()
                if result:
                    print(f"Tag result: {result}")
                    return result
                print(f"Tag not found, retrying... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            
            print(f"Tag {tag_id} not found after {self.max_retries} attempts")
            return None

        except mysql.connector.Error as err:
            print(f"MySQL Error getting tag:")
            print(f"Error Code: {err.errno}")
            print(f"Error Message: {err.msg}")
            print(f"SQL State: {err.sqlstate}")
            return None
        except Exception as e:
            print(f"Unexpected error getting tag: {str(e)}")
            return None

    def get_all_tags(self):
        try:
            print("Executing get_all_tags query...")
            
            def get_tags_with_retry():
                self.cursor.execute("SELECT * FROM tags")
                return self.cursor.fetchall()

            # Probeer de tags meerdere keren op te halen
            for attempt in range(self.max_retries):
                results = get_tags_with_retry()
                if results is not None:
                    print(f"Found {len(results)} tags")
                    return results
                print(f"No results, retrying... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            
            print("No tags found after all attempts")
            return []

        except mysql.connector.Error as err:
            print(f"MySQL Error getting all tags: {err}")
            return []
        except Exception as e:
            print(f"Unexpected error getting all tags: {str(e)}")
            return []

    def add_log(self, tag_id, username, message, latitude, longitude):
        try:
            print(f"Adding log for tag {tag_id} by {username}")
            
            # Verify tag exists first
            if not self.get_tag(tag_id):
                print(f"Tag {tag_id} not found, cannot add log")
                return False

            self.cursor.execute(
                "INSERT INTO logs (tag_id, username, message, latitude, longitude) VALUES (%s, %s, %s, %s, %s)",
                (tag_id, username, message, latitude, longitude)
            )
            self.conn.commit()
            print("Log added successfully")
            
            # Verify log was added
            def verify_log():
                self.cursor.execute(
                    "SELECT * FROM logs WHERE tag_id = %s AND username = %s ORDER BY timestamp DESC LIMIT 1",
                    (tag_id, username)
                )
                return self.cursor.fetchone() is not None

            if self.wait_for_operation("Log verification", verify_log):
                return True
            return False

        except mysql.connector.Error as err:
            print(f"MySQL Error adding log: {err}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Unexpected error adding log: {str(e)}")
            self.conn.rollback()
            return False

    def get_logs(self, tag_id):
        try:
            print(f"Getting logs for tag {tag_id}")
            
            def get_logs_with_retry():
                self.cursor.execute("SELECT * FROM logs WHERE tag_id = %s ORDER BY timestamp DESC", (tag_id,))
                return self.cursor.fetchall()

            # Probeer de logs meerdere keren op te halen
            for attempt in range(self.max_retries):
                results = get_logs_with_retry()
                if results is not None:
                    print(f"Found {len(results)} logs")
                    return results
                print(f"No results, retrying... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            
            print("No logs found after all attempts")
            return []

        except mysql.connector.Error as err:
            print(f"MySQL Error getting logs: {err}")
            return []
        except Exception as e:
            print(f"Unexpected error getting logs: {str(e)}")
            return []

    def get_all_logs(self):
        try:
            print("Getting all logs")
            
            def get_all_logs_with_retry():
                self.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
                return self.cursor.fetchall()

            # Probeer de logs meerdere keren op te halen
            for attempt in range(self.max_retries):
                results = get_all_logs_with_retry()
                if results is not None:
                    print(f"Found {len(results)} logs")
                    return results
                print(f"No results, retrying... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            
            print("No logs found after all attempts")
            return []

        except mysql.connector.Error as err:
            print(f"MySQL Error getting all logs: {err}")
            return []
        except Exception as e:
            print(f"Unexpected error getting all logs: {str(e)}")
            return []

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
            print("Database connection closed") 