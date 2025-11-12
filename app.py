import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_manager import DataManager
from access_control import AdminContext, AdminRole, AccessControl
from query_parser import QueryExecutor, QueryParser

# Page configuration
st.set_page_config(
    page_title="Dumroo Admin - NLQ System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 20px; }
    .stTitle { color: #1f77b4; }
    .query-box { background-color: #f0f2f6; padding: 15px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'admin_context' not in st.session_state:
    st.session_state.admin_context = None

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'data_manager' not in st.session_state:
    try:
        st.session_state.data_manager = DataManager("data/data_sample_data.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please ensure data/sample_data.csv exists.")

def setup_admin_context(admin_role_name: str, grades: list, classes: list):
    """Setup admin context based on selected role"""
    role_mapping = {
        "Super Admin": AdminRole.SUPER_ADMIN,
        "Grade Admin": AdminRole.GRADE_ADMIN,
        "Class Admin": AdminRole.CLASS_ADMIN
    }
    
    return AdminContext(
        admin_id="admin_001",
        admin_name="Demo Admin",
        role=role_mapping[admin_role_name],
        assigned_grades=grades,
        assigned_classes=classes
    )

def format_results(df: pd.DataFrame) -> str:
    """Format results nicely"""
    if df.empty:
        return "No results found matching your query."
    
    # Select relevant columns for display
    display_columns = [col for col in ['student_name', 'grade', 'class', 'submission_status', 
                                       'homework_score', 'quiz_name', 'quiz_score', 'quiz_date', 'submission_date'] 
                      if col in df.columns]
    
    return df[display_columns].to_string(index=False)

# Sidebar - Admin Configuration
st.sidebar.title("⚙️ Admin Configuration")
st.sidebar.divider()

admin_role = st.sidebar.selectbox(
    "Select Admin Role",
    ["Super Admin", "Grade Admin", "Class Admin"],
    help="Choose your admin role to control data access"
)

if admin_role == "Super Admin":
    grades = st.sidebar.info("✓ Full access to all grades")
    classes = []
elif admin_role == "Grade Admin":
    grades = st.sidebar.multiselect(
        "Assigned Grades",
        [8, 9],
        default=[8],
        help="Select grades you can access"
    )
    classes = []
else:  # Class Admin
    grades = st.sidebar.multiselect(
        "Assigned Grades",
        [8, 9],
        default=[8],
        help="Select grades you can access"
    )
    classes = st.sidebar.multiselect(
        "Assigned Classes",
        ["A", "B", "C"],
        default=["A"],
        help="Select classes you can access"
    )

# Setup admin context
if admin_role == "Super Admin":
    st.session_state.admin_context = setup_admin_context(admin_role, [8, 9], [])
else:
    st.session_state.admin_context = setup_admin_context(admin_role, grades if grades else [], classes if classes else [])

st.sidebar.divider()
st.sidebar.info(f"👤 **Current User:** Demo Admin\n\n📊 **Role:** {admin_role}")

# Main content
st.title("🚀 Dumroo Admin - Natural Language Query System")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Query Interface", "Example Queries", "Data Preview", "Documentation"])

with tab1:
    st.header("Ask Questions in Plain English")
    st.markdown("Type your question and the AI system will fetch relevant data with your access permissions applied.")
    
    # Query input
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Enter your query:",
            placeholder="e.g., Which students haven't submitted their homework yet?",
            key="query_input"
        )
    
    with col2:
        submit_button = st.button("🔍 Search", use_container_width=True)
    
    if submit_button and query:
        try:
            # Create access control and query executor
            access_control = AccessControl(st.session_state.admin_context)
            query_executor = QueryExecutor(st.session_state.data_manager, access_control)
            
            # Execute query
            with st.spinner("Processing your query..."):
                result_df = query_executor.execute(query)
            
            # Display results
            st.subheader("📋 Results")
            if result_df.empty:
                st.warning("No results found matching your query and access permissions.")
            else:
                st.success(f"✓ Found {len(result_df)} record(s)")
                st.dataframe(result_df, use_container_width=True)
                
                # Additional stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Results", len(result_df))
                with col2:
                    if 'quiz_score' in result_df.columns:
                        avg_score = result_df[result_df['quiz_score'] > 0]['quiz_score'].mean()
                        st.metric("Avg Quiz Score", f"{avg_score:.2f}" if avg_score > 0 else "N/A")
                with col3:
                    if 'submission_status' in result_df.columns:
                        pending = (result_df['submission_status'] == 'pending').sum()
                        st.metric("Pending Submissions", pending)
                
                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                'query': query,
                'timestamp': datetime.now(),
                'results': len(result_df)
            })
        
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")

with tab2:
    st.header("📝 Example Queries")
    
    examples = [
        {
            "title": "Pending Submissions",
            "queries": [
                "Which students haven't submitted their homework yet?",
                "Show me pending submissions for Grade 8",
                "Who hasn't submitted in class A?"
            ]
        },
        {
            "title": "Performance Analysis",
            "queries": [
                "Show me performance data for Grade 8 from last week",
                "What are the quiz scores for students in Grade 9?",
                "Which students have low scores?",
                "Performance data from last week"
            ]
        },
        {
            "title": "Quiz Scheduling",
            "queries": [
                "List all upcoming quizzes scheduled for next week",
                "Show upcoming quizzes for Grade 8",
                "What quizzes are scheduled?",
                "Next week's quiz schedule"
            ]
        }
    ]
    
    for example_group in examples:
        st.subheader(f"🔹 {example_group['title']}")
        for i, example_query in enumerate(example_group['queries'], 1):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.code(example_query)

with tab3:
    st.header("📊 Data Preview")
    
    try:
        data = st.session_state.data_manager.get_all_data()
        access_control = AccessControl(st.session_state.admin_context)
        filtered_data = access_control.apply_access_control(data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Students", len(filtered_data))
        with col2:
            st.metric("Grades Available", filtered_data['grade'].nunique())
        with col3:
            st.metric("Pending Submissions", (filtered_data['submission_status'] == 'pending').sum())
        
        st.subheader("Current Dataset")
        st.dataframe(filtered_data, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

with tab4:
    st.header("📖 Documentation")
    
    st.markdown("""
    ## System Overview
    
    The Dumroo Admin Natural Language Query System allows administrators to ask questions in plain English 
    and get instant access to student data, quiz information, and submission status.
    
    ### Key Features
    
    ✅ **Natural Language Processing** - Type queries in simple English
    
    ✅ **Role-Based Access Control** - Admins see only data they're authorized for
    
    ✅ **Performance Analytics** - View quiz scores and student progress
    
    ✅ **Submission Tracking** - Monitor homework and assignment submissions
    
    ✅ **Quiz Management** - Schedule and track quizzes
    
    ### Supported Query Types
    
    1. **Pending Submissions**
       - "Which students haven't submitted their homework yet?"
       - "Show me pending submissions"
    
    2. **Performance Data**
       - "Show me performance data for Grade 8 from last week"
       - "Quiz scores for Grade 9"
    
    3. **Upcoming Quizzes**
       - "List all upcoming quizzes scheduled for next week"
       - "What quizzes are coming up?"
    
    ### Access Control Levels
    
    - **Super Admin**: Full access to all data
    - **Grade Admin**: Access to assigned grades only
    - **Class Admin**: Access to assigned grades and classes
    
    ### Data Privacy
    
    All queries are subject to role-based access control. Sensitive columns are filtered based on admin role.
    All access is logged for audit purposes.
    """)
    
    st.subheader("🏗️ Architecture")
    st.markdown("""
    ```
    User Query (Natural Language)
         ↓
    Query Parser (Regex + Pattern Matching)
         ↓
    Query Executor (Business Logic)
         ↓
    Data Manager (CSV/Database)
         ↓
    Access Control Filter
         ↓
    Results Display
    ```
    """)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📋 Queries Executed: {len(st.session_state.conversation_history)}")
with col2:
    st.caption(f"👤 Logged in as: Demo Admin ({st.session_state.admin_context.role.value})")
with col3:
    st.caption(f"⏱️ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")