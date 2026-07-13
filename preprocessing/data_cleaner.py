import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import h3
import logging
from pathlib import Path
import sys

# Add the root directory to path to import database module
sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.sqlite import DatabaseManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataCleaner:
    def __init__(self, raw_data_dir: str = "data/raw", db_path: str = "database/road_risk.db"):
        self.raw_data_dir = Path(raw_data_dir)
        self.db_manager = DatabaseManager(db_path)
        
    def load_data(self):
        """Loads all relevant dataset files."""
        logging.info("Loading raw datasets...")
        try:
            # Using 'latin-1' or 'ISO-8859-1' due to french characters in the dataset
            self.characteristics = pd.read_csv(self.raw_data_dir / 'caracteristics.csv', encoding='latin-1', low_memory=False)
            self.places = pd.read_csv(self.raw_data_dir / 'places.csv', encoding='latin-1', low_memory=False)
            self.vehicles = pd.read_csv(self.raw_data_dir / 'vehicles.csv', encoding='latin-1', low_memory=False)
            self.users = pd.read_csv(self.raw_data_dir / 'users.csv', encoding='latin-1', low_memory=False)
            logging.info("Datasets loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading datasets: {e}")
            raise

    def clean_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes Latitude and Longitude."""
        logging.info("Cleaning coordinate data...")
        
        # Replace commas with dots if they are strings, convert to numeric
        for col in ['lat', 'long']:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Datasets sometimes have lat/long multiplied by 100000
        # If absolute value is > 90, it's highly likely they are unscaled
        df.loc[df['lat'].abs() > 90, 'lat'] = df['lat'] / 100000
        df.loc[df['long'].abs() > 90, 'long'] = df['long'] / 100000
        
        # Drop rows with NaN or exactly 0 (which are invalid/missing in this context)
        df = df.dropna(subset=['lat', 'long'])
        df = df[(df['lat'] != 0) & (df['long'] != 0)]
        
        # Filter for Metropolitan France Bounding Box to remove anomalies
        # roughly: Lat 41.0 to 51.5, Long -5.5 to 10.0
        df = df[(df['lat'] >= 41.0) & (df['lat'] <= 51.5) & (df['long'] >= -5.5) & (df['long'] <= 10.0)]
        
        logging.info(f"Coordinates cleaned. Valid records with GPS: {len(df)}")
        return df

    def merge_datasets(self) -> pd.DataFrame:
        """Merges characteristics and places on Num_Acc."""
        logging.info("Merging datasets...")
        
        # For base risk mapping, we primarily need characteristics and places
        # Vehicles and Users can be joined later or aggregated
        # Let's aggregate severe injuries / fatalities from users to get accident severity
        users_severity = self.users.groupby('Num_Acc')['grav'].apply(
            lambda x: (x == 2).sum()  # grav == 2 corresponds to killed (tué) in French dataset
        ).reset_index(name='fatalities')
        
        merged_df = pd.merge(self.characteristics, self.places, on='Num_Acc', how='inner')
        merged_df = pd.merge(merged_df, users_severity, on='Num_Acc', how='left')
        
        merged_df['fatalities'] = merged_df['fatalities'].fillna(0)
        
        # Clean coordinates immediately after merge
        merged_df = self.clean_coordinates(merged_df)
        
        return merged_df

    def create_geodataframe(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        """Converts Pandas DataFrame to GeoPandas GeoDataFrame."""
        logging.info("Converting to GeoDataFrame...")
        geometry = [Point(xy) for xy in zip(df['long'], df['lat'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        return gdf

    def generate_h3_index(self, df: pd.DataFrame, resolution: int = 8) -> pd.DataFrame:
        """Generates H3 hexagonal index from coordinates."""
        logging.info(f"Generating H3 index at resolution {resolution}...")
        df['h3_index'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['long'], resolution), axis=1)
        return df

    def run_pipeline(self):
        """Executes the full cleaning and merging pipeline."""
        self.load_data()
        
        df_merged = self.merge_datasets()
        
        # Generate H3 index
        df_final = self.generate_h3_index(df_merged, resolution=8)
        
        # Drop the geometry column temporarily to save to SQLite (SQLite doesn't natively support geometry types well without SpatiaLite)
        # We store the WKT or just Lat/Lon so we can reconstruct it later
        
        logging.info("Saving processed data to SQLite...")
        self.db_manager.save_dataframe(df_final, "processed_accidents")
        
        logging.info("Data Engineering Phase 1 Complete!")
        self.db_manager.close()
        
        return df_final

if __name__ == "__main__":
    cleaner = DataCleaner()
    processed_df = cleaner.run_pipeline()
    print(f"Sample data:\n{processed_df.head()}")
