import sqlite3
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DatabaseManager:
    """
    Handles SQLite database operations for storing processed data,
    risk zones, and predictions.
    """
    def __init__(self, db_path: str = "road_risk.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        logging.info(f"Connected to SQLite database at {self.db_path}")
        self.initialize_schema()

    def initialize_schema(self):
        """Creates the required tables if they don't exist."""
        schema_queries = [
            """CREATE TABLE IF NOT EXISTS accidents (
                Num_Acc TEXT PRIMARY KEY, h3_index TEXT, lat REAL, long REAL, 
                severity_score REAL, date_time TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS risk_zones (
                h3_index TEXT PRIMARY KEY, geometry TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT, Num_Acc TEXT, vehicle_type TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, Num_Acc TEXT, user_category TEXT, severity INTEGER
            )""",
            """CREATE TABLE IF NOT EXISTS zone_statistics (
                h3_index TEXT PRIMARY KEY, accident_count INTEGER, fatal_count INTEGER,
                rain_percentage REAL, night_percentage REAL, road_surface_score REAL,
                severity_mean REAL, peak_hour INTEGER, peak_month INTEGER
            )""",
            """CREATE TABLE IF NOT EXISTS risk_scores (
                h3_index TEXT PRIMARY KEY, risk_score REAL, risk_level TEXT, 
                risk_color TEXT, explanation TEXT, ai_prediction REAL
            )""",
            """CREATE TABLE IF NOT EXISTS simulation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, 
                vehicle_id TEXT, lat REAL, long REAL, h3_index TEXT, alert_triggered TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, h3_index TEXT, model_version TEXT, 
                predicted_risk REAL, timestamp TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle TEXT, zone TEXT, 
                risk REAL, time TEXT, type TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS vehicle_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT, timestamp TEXT, 
                latitude REAL, longitude REAL, speed REAL, heading REAL, 
                risk REAL, zone TEXT, status TEXT
            )"""
        ]
        try:
            cursor = self.conn.cursor()
            for query in schema_queries:
                cursor.execute(query)
            self.conn.commit()
            logging.info("SQLite schema initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing schema: {e}")
            raise

    def save_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
        """
        Saves a Pandas DataFrame to the SQLite database.
        """
        try:
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
            logging.info(f"Successfully saved {len(df)} records to table '{table_name}'.")
        except Exception as e:
            logging.error(f"Error saving DataFrame to table '{table_name}': {e}")
            raise

    def load_dataframe(self, query: str) -> pd.DataFrame:
        """
        Loads data from the SQLite database into a Pandas DataFrame.
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            logging.info(f"Successfully loaded {len(df)} records using query.")
            return df
        except Exception as e:
            logging.error(f"Error loading DataFrame with query '{query}': {e}")
            raise

    def execute_query(self, query: str):
        """
        Executes a direct SQL query (e.g., CREATE TABLE, DROP TABLE).
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            logging.info("Query executed successfully.")
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()
        logging.info("Database connection closed.")
