from typing import Dict, List, Any
import pandas as pd
from enum import Enum

class AdminRole(Enum):
    """Admin role levels"""
    SUPER_ADMIN = "super_admin"
    GRADE_ADMIN = "grade_admin"
    CLASS_ADMIN = "class_admin"
    REGION_ADMIN = "region_admin"

class AdminContext:
    """Represents admin user context and permissions"""
    
    def __init__(
        self,
        admin_id: str,
        admin_name: str,
        role: AdminRole,
        assigned_grades: List[int] = None,
        assigned_classes: List[str] = None,
        assigned_region: str = None
    ):
        self.admin_id = admin_id
        self.admin_name = admin_name
        self.role = role
        self.assigned_grades = assigned_grades or []
        self.assigned_classes = assigned_classes or []
        self.assigned_region = assigned_region
    
    def can_access_grade(self, grade: int) -> bool:
        """Check if admin can access a specific grade"""
        if self.role == AdminRole.SUPER_ADMIN:
            return True
        return grade in self.assigned_grades
    
    def can_access_class(self, grade: int, class_name: str) -> bool:
        """Check if admin can access a specific class"""
        if self.role == AdminRole.SUPER_ADMIN:
            return True
        if self.role == AdminRole.GRADE_ADMIN:
            return self.can_access_grade(grade)
        if self.role == AdminRole.CLASS_ADMIN:
            return grade in self.assigned_grades and class_name in self.assigned_classes
        return False

class AccessControl:
    """Manages role-based access control"""
    
    def __init__(self, admin_context: AdminContext):
        self.admin = admin_context
    
    def filter_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter dataframe based on admin permissions"""
        if self.admin.role == AdminRole.SUPER_ADMIN:
            return df.copy()
        
        # Filter by assigned grades
        filtered_df = df[df['grade'].isin(self.admin.assigned_grades)].copy()
        
        # Filter by assigned classes if applicable
        if self.admin.assigned_classes:
            filtered_df = filtered_df[filtered_df['class'].isin(self.admin.assigned_classes)]
        
        return filtered_df
    
    def filter_sensitive_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove sensitive columns based on role"""
        df = df.copy()
        
        # Only super admin can see admin-level info
        if self.admin.role != AdminRole.SUPER_ADMIN:
            sensitive_columns = ['student_id']  # Add more as needed
            df = df.drop(columns=[col for col in sensitive_columns if col in df.columns])
        
        return df
    
    def apply_access_control(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all access control rules"""
        df = self.filter_dataframe(df)
        df = self.filter_sensitive_columns(df)
        return df
    
    def log_access(self, query: str, result_count: int):
        """Log admin access for audit purposes"""
        print(f"[AUDIT] Admin {self.admin.admin_name} ({self.admin.admin_id}) "
              f"executed query: '{query}' - Results: {result_count}")