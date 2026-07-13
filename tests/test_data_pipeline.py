import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from preprocessing.data_cleaner import DataCleaner

@pytest.fixture
def dummy_data():
    return pd.DataFrame({
        'Num_Acc': [1, 2, 3, 4],
        'lat': [48.8566 * 100000, 0, 43.2965, "45,7640"], # Paris scaled, Invalid, Marseille normal, Lyon string with comma
        'long': [2.3522 * 100000, 0, 5.3698, "4,8357"],
        'grav': [2, 1, 3, 2]
    })

def test_clean_coordinates(dummy_data):
    cleaner = DataCleaner(db_path=":memory:") # Use in-memory SQLite for tests
    cleaned_df = cleaner.clean_coordinates(dummy_data)
    
    # Assert invalid coordinates (0, 0) are dropped
    assert len(cleaned_df) == 3
    
    # Assert strings with commas are converted to floats
    assert cleaned_df.loc[cleaned_df['Num_Acc'] == 4, 'lat'].values[0] == 45.7640
    
    # Assert scaled coordinates are downscaled
    assert cleaned_df.loc[cleaned_df['Num_Acc'] == 1, 'lat'].values[0] == pytest.approx(48.8566)

def test_h3_generation():
    cleaner = DataCleaner(db_path=":memory:")
    df = pd.DataFrame({'lat': [48.8566], 'long': [2.3522]})
    h3_df = cleaner.generate_h3_index(df, resolution=8)
    
    assert 'h3_index' in h3_df.columns
    assert type(h3_df.loc[0, 'h3_index']) == str
    assert len(h3_df.loc[0, 'h3_index']) > 5
