import pyodbc
from .config import DB_CONFIG

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            conn_str = (
                f"DRIVER={DB_CONFIG['DRIVER']};"
                f"SERVER={DB_CONFIG['SERVER']};"
                f"DATABASE={DB_CONFIG['DATABASE']};"
                f"UID={DB_CONFIG['UID']};"
                f"PWD={DB_CONFIG['PWD']};"
                f"TrustServerCertificate={DB_CONFIG['TrustServerCertificate']}"
            )
            self.connection = pyodbc.connect(conn_str)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def execute_query(self, query):
        """Execute SQL query and return results"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            results = cursor.fetchall()
            
            return {
                "success": True,
                "columns": columns,
                "data": [list(row) for row in results],
                "row_count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
