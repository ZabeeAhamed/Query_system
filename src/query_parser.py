from typing import Dict, Any, Tuple
import re
from datetime import datetime, timedelta
import pandas as pd

class QueryParser:
    """Parses natural language queries to extract structured information"""
    
    def __init__(self):
        self.query_patterns = {
            'pending_submissions': [
                r"(who|which students?)\s+(?:haven't?|have not|didn't)\s+submit",
                r"pending\s+(?:submissions?|homework)",
                r"students?\s+with\s+no\s+submission"
            ],
            'performance': [
                r"performance\s+data",
                r"quiz\s+scores?",
                r"student\s+(?:performance|progress)",
                r"top\s+students?",
                r"low\s+scores?"
            ],
            'upcoming_quizzes': [
                r"upcoming\s+quizzes?",
                r"scheduled\s+quizzes?",
                r"next\s+(?:week|quiz)",
                r"quiz\s+schedule"
            ],
            'homework': [
                r"homework",
                r"assignment",
                r"submission"
            ],
            'grade_filter': [
                r"grade\s+(\d+)",
                r"(\d+)(?:th|nd|rd|st)\s+grade"
            ],
            'class_filter': [
                r"class\s+([A-Za-z])",
                r"section\s+([A-Za-z])"
            ],
            'date_filter': [
                r"(this\s+week|last\s+week|next\s+week)",
                r"from\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})",
                r"between\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})\s+and\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
            ]
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured format"""
        query_lower = query.lower()
        result = {
            'query_type': None,
            'filters': {
                'grade': None,
                'class': None,
                'date_range': None
            },
            'raw_query': query
        }
        
        # Detect query type
        for query_type, patterns in self.query_patterns.items():
            if query_type.startswith('grade_filter') or query_type.startswith('class_filter') or query_type.startswith('date_filter'):
                continue
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    result['query_type'] = query_type
                    break
            if result['query_type']:
                break
        
        # Extract filters
        # Grade filter
        grade_match = re.search(self.query_patterns['grade_filter'][0], query_lower)
        if grade_match:
            result['filters']['grade'] = int(grade_match.group(1))
        
        # Class filter
        class_match = re.search(self.query_patterns['class_filter'][0], query_lower)
        if class_match:
            result['filters']['class'] = class_match.group(1).upper()
        
        # Date filter
        date_match = re.search(self.query_patterns['date_filter'][0], query_lower)
        if date_match:
            result['filters']['date_range'] = self._parse_date_reference(date_match.group(1))
        
        return result
    
    def _parse_date_reference(self, date_ref: str) -> Tuple[datetime, datetime]:
        """Convert date references like 'this week', 'last week' to date ranges"""
        today = datetime.now()
        
        if 'this week' in date_ref:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif 'last week' in date_ref:
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
        elif 'next week' in date_ref:
            start = today + timedelta(days=7 - today.weekday())
            end = start + timedelta(days=6)
        else:
            start = today - timedelta(days=7)
            end = today
        
        return start, end

class QueryExecutor:
    """Executes parsed queries against the data"""
    
    def __init__(self, data_manager, access_control):
        self.data_manager = data_manager
        self.access_control = access_control
        self.parser = QueryParser()
    
    def execute(self, query: str) -> pd.DataFrame:
        """Execute a natural language query"""
        parsed = self.parser.parse_query(query)
        result = pd.DataFrame()
        
        if parsed['query_type'] == 'pending_submissions':
            result = self._get_pending_submissions(parsed['filters'])
        elif parsed['query_type'] == 'performance':
            result = self._get_performance_data(parsed['filters'])
        elif parsed['query_type'] == 'upcoming_quizzes':
            result = self._get_upcoming_quizzes(parsed['filters'])
        
        # Apply access control
        result = self.access_control.apply_access_control(result)
        
        # Log access
        self.access_control.log_access(query, len(result))
        
        return result
    
    def _get_pending_submissions(self, filters: Dict) -> pd.DataFrame:
        """Get pending submissions"""
        result = self.data_manager.get_pending_submissions(filters.get('grade'))
        return result
    
    def _get_performance_data(self, filters: Dict) -> pd.DataFrame:
        """Get performance data"""
        if filters.get('grade'):
            result = self.data_manager.get_students_by_grade(filters['grade'])
        else:
            result = self.data_manager.get_all_data()
        
        if filters.get('date_range'):
            start, end = filters['date_range']
            result = result[
                (result['quiz_date'] >= start) & (result['quiz_date'] <= end)
            ]
        
        return result
    
    def _get_upcoming_quizzes(self, filters: Dict) -> pd.DataFrame:
        """Get upcoming quizzes"""
        today = datetime.now()
        result = self.data_manager.get_all_data()
        
        # Filter for future quizzes
        result = result[result['quiz_date'] >= today]
        
        if filters.get('grade'):
            result = result[result['grade'] == filters['grade']]
        
        if filters.get('class'):
            result = result[result['class'] == filters['class']]
        
        return result.sort_values('quiz_date')