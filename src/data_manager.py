import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os

class DataManager:
    """Manages data loading and basic operations"""
    
    def __init__(self, csv_path: str = "data/data_sample_data.csv"):
        self.csv_path = csv_path
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV"""
        if os.path.exists(self.csv_path):
            self.data = pd.read_csv(self.csv_path)
            # Convert date columns to datetime
            date_columns = ['quiz_date', 'submission_date', 'last_activity']
            for col in date_columns:
                if col in self.data.columns:
                    self.data[col] = pd.to_datetime(self.data[col], errors='coerce')
        else:
            raise FileNotFoundError(f"Data file not found: {self.csv_path}")
    
    def get_all_data(self) -> pd.DataFrame:
        """Get all data"""
        return self.data.copy()
    
    def get_students_by_grade(self, grade: int) -> pd.DataFrame:
        """Get all students in a specific grade"""
        return self.data[self.data['grade'] == grade].copy()
    
    def get_students_by_class(self, grade: int, class_name: str) -> pd.DataFrame:
        """Get students in a specific grade and class"""
        return self.data[(self.data['grade'] == grade) & (self.data['class'] == class_name)].copy()
    
    def get_pending_submissions(self, grade: int = None) -> pd.DataFrame:
        """Get students with pending submissions"""
        result = self.data[self.data['submission_status'] == 'pending'].copy()
        if grade is not None:
            result = result[result['grade'] == grade]
        return result
    
    def get_students_by_performance(self, grade: int, min_score: float = 0, max_score: float = 100) -> pd.DataFrame:
        """Get students by quiz score range"""
        result = self.data[self.data['grade'] == grade].copy()
        result = result[(result['quiz_score'] >= min_score) & (result['quiz_score'] <= max_score)]
        return result
    
    def get_data_from_date_range(self, start_date: datetime, end_date: datetime, column: str = 'quiz_date') -> pd.DataFrame:
        """Get data within a date range"""
        if column not in self.data.columns:
            return pd.DataFrame()
        
        mask = (self.data[column] >= start_date) & (self.data[column] <= end_date)
        return self.data[mask].copy()
    
    def search_by_name(self, name: str) -> pd.DataFrame:
        """Search students by name"""
        return self.data[self.data['student_name'].str.contains(name, case=False, na=False)].copy()