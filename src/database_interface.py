from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any

class DatabaseInterface(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    def get_students(self, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """Fetch students with optional filters"""
        pass
    
    @abstractmethod
    def get_submissions(self, student_id: int = None) -> pd.DataFrame:
        """Fetch submission data"""
        pass
    
    @abstractmethod
    def get_quizzes(self, grade: int = None) -> pd.DataFrame:
        """Fetch quiz data"""
        pass
    
    @abstractmethod
    def log_query(self, admin_id: str, query: str, result_count: int):
        """Log query execution for audit"""
        pass

class CSVDatabaseAdapter(DatabaseInterface):
    """CSV-based database adapter"""
    
    def __init__(self, csv_path: str== "data/data_sample_data.csv"):
        self.csv_path = csv_path
        self.data = None
    
    def connect(self):
        """Load CSV file"""
        import pandas as pd
        self.data = pd.read_csv(self.csv_path)
    
    def disconnect(self):
        """Close connection"""
        self.data = None
    
    def get_students(self, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """Get students with filters"""
        result = self.data.copy()
        if filters:
            if 'grade' in filters:
                result = result[result['grade'] == filters['grade']]
            if 'class' in filters:
                result = result[result['class'] == filters['class']]
        return result
    
    def get_submissions(self, student_id: int = None) -> pd.DataFrame:
        """Get submissions"""
        result = self.data[['student_id', 'student_name', 'submission_status', 'submission_date']].copy()
        if student_id:
            result = result[result['student_id'] == student_id]
        return result
    
    def get_quizzes(self, grade: int = None) -> pd.DataFrame:
        """Get quizzes"""
        result = self.data[['quiz_name', 'quiz_date', 'quiz_score', 'grade']].copy()
        if grade:
            result = result[result['grade'] == grade]
        return result
    
    def log_query(self, admin_id: str, query: str, result_count: int):
        """Log query execution"""
        print(f"[DB_LOG] Admin: {admin_id}, Query: {query}, Results: {result_count}")

# Future: PostgreSQL, MongoDB adapters can be added here