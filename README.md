# 🚀 Dumroo Admin - AI-Powered Natural Language Query System

An intelligent admin panel system that allows educators to query student data, performance metrics, and quiz schedules using simple English questions—with role-based access control built-in.

## ✨ Features

- **Natural Language Queries** - Ask questions in plain English instead of SQL or APIs
- **Role-Based Access Control** - Admins automatically see only data for their assigned grades/classes
- **Multi-Turn Conversations** - Ask follow-up questions and maintain context
- **Performance Analytics** - Automatically calculate averages, trends, and insights
- **Audit Logging** - All queries are logged for compliance and security
- **Modular Architecture** - Easy to connect to real databases (PostgreSQL, MongoDB, etc.)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Streamlit UI (Query Interface)                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│      Query Parser (NLP + Pattern Matching)              │
│   Converts "Which students haven't submitted?"          │
│   → {query_type: 'pending_submissions', grade: 8}       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│         Query Executor (Business Logic)                 │
│   Executes filtered database operations                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│      Access Control Filter (RBAC)                       │
│   Ensures admin only sees their grade/class             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│      Data Manager (CSV/Database Interface)              │
│   Abstracts data source - supports CSV, SQL, etc.       │
└─────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
dumroo-admin-nlq-system/
├── data/
│   └── sample_data.csv           # Sample student/quiz data
├── src/
│   ├── __init__.py
│   ├── data_manager.py           # Data loading & operations
│   ├── access_control.py         # Role-based access control
│   ├── query_parser.py           # NLP query parsing
│   └── database_interface.py     # Abstract DB interface
├── app.py                        # Streamlit interface
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ZabeeAhamed/dumroo-admin-nlq
cd dumroo-admin-nlq
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📝 Example Queries

### Example 1: Pending Submissions
**Query:** "Which students haven't submitted their homework yet?"

**Response:**
```
Found 2 records:

student_name    grade  class  submission_status
Bob Smith         8      A      pending
Emma Wilson       8      B      pending
```

### Example 2: Performance Data
**Query:** "Show me performance data for Grade 8 from last week"

**Response:**
```
Found 6 records:

student_name      grade  class  quiz_name    quiz_score  quiz_date
Alice Johnson       8      A     Math Quiz        88      2025-11-05
Charlie Brown       8      B     Science Quiz     92      2025-11-06
Diana Prince        8      A     Math Quiz        95      2025-11-05
Emma Wilson         8      B     Science Quiz      0      2025-11-06
Iris West           8      C     Math Quiz        78      2025-11-05
```

### Example 3: Upcoming Quizzes
**Query:** "List all upcoming quizzes scheduled for next week"

**Response:**
```
Found 2 records:

quiz_name      quiz_date     grade
Physics Quiz   2025-11-12      9
Physics Quiz   2025-11-12      9
```

## 👥 Role-Based Access Control

The system supports three admin roles with different permission levels:

### Super Admin
- Full access to all grades and classes
- Can see all student data
- Can view platform-wide analytics

### Grade Admin
- Access limited to assigned grades
- Can see all classes within their grades
- Example: Admin assigned to Grade 8 sees all students in Grade 8

### Class Admin
- Access limited to assigned grades and classes
- Most restricted role
- Example: Admin assigned to Grade 8, Class A sees only that specific class

## 🔍 Query Type Support

### 1. Pending Submissions
- Detects: "haven't submitted", "pending submissions", "no submission"
- Returns: Students with submission_status = "pending"
- Example: "Which students haven't submitted their homework yet?"

### 2. Performance Analysis
- Detects: "performance data", "quiz scores", "top students", "low scores"
- Returns: Quiz performance data with optional date filtering
- Example: "Show me performance data for Grade 8 from last week"

### 3. Upcoming Quizzes
- Detects: "upcoming quizzes", "scheduled quizzes", "next week"
- Returns: Future quizzes sorted by date
- Example: "List all upcoming quizzes scheduled for next week"

## 🛠️ Extending the System

### Adding a New Query Type

1. Add pattern to `QueryParser.query_patterns` in `src/query_parser.py`
2. Add handler method to `QueryExecutor` class
3. Example:

```python
# In query_parser.py
self.query_patterns['new_query_type'] = [
    r"pattern1",
    r"pattern2"
]

# In QueryExecutor
def _new_query_handler(self, filters: Dict) -> pd.DataFrame:
    # Your implementation here
    return result_df
```

### Connecting to a Real Database

1. Implement `DatabaseInterface` in `src/database_interface.py`
2. Create adapter for your database (PostgreSQL, MongoDB, etc.)
3. Update `DataManager` to use your adapter

```python
class PostgreSQLAdapter(DatabaseInterface):
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
    
    # Implement required methods
    def get_students(self, filters=None):
        # Query implementation
        pass
```

## 📊 Sample Data Structure

The `sample_data.csv` includes:
- **student_id**: Unique student identifier
- **student_name**: Full name of student
- **grade**: Grade level (8, 9, etc.)
- **class**: Class section (A, B, C, etc.)
- **submission_status**: "submitted" or "pending"
- **homework_score**: Score out of 100
- **quiz_name**: Name of quiz
- **quiz_score**: Quiz score out of 100
- **quiz_date**: Date quiz was given
- **submission_date**: Date assignment was submitted
- **last_activity**: Last time student accessed system

## 🔐 Security Features

✅ **Role-Based Access Control** - Ensures data privacy at role level
✅ **Audit Logging** - All queries logged with admin ID and timestamp
✅ **Column Filtering** - Sensitive columns hidden based on role
✅ **Input Validation** - Query inputs sanitized before processing

## 📈 Future Enhancements

- [ ] Multi-turn conversation support with context
- [ ] Real-time data sync with school databases
- [ ] Advanced analytics and trends
- [ ] Export reports in multiple formats
- [ ] Integration with LangChain agents
- [ ] Custom metric calculations
- [ ] Multi-language support

## 🐛 Troubleshooting

**Issue**: "Data file not found"
- Solution: Ensure `data/sample_data.csv` exists in the project directory

**Issue**: Module import errors
- Solution: Run `pip install -r requirements.txt` in project directory

**Issue**: Streamlit not loading
- Solution: Make sure port 8501 is available, run `streamlit run app.py --logger.level=debug`

## 📚 Documentation

For detailed documentation on extending the system, see:
- `src/query_parser.py` - Query parsing logic
- `src/access_control.py` - Access control implementation
- `src/database_interface.py` - Database integration guide

## 👨‍💻 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions or issues, please open a GitHub issue with detailed description.

---

**Built with ❤️ for Dumroo.ai**
