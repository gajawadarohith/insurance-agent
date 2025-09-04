#!/usr/bin/env python3

# Import MCP components
from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import json
from typing import Dict, List, Any

# Initialize the MCP server
mcp = FastMCP("Insurance Database Server")

# Database path
DB_PATH = "insurance_db.sqlite"

def connect_to_db():
    """Connect to SQLite database"""
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file '{DB_PATH}' not found!")
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")

# Define a resource to fetch the database schema
@mcp.resource("schema://insurance")
def get_schema() -> str:
    """Provide the insurance database schema as a resource"""
    conn = connect_to_db()
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        conn.close()
        return "\n".join(sql[0] for sql in schema if sql[0])
    except Exception as e:
        conn.close()
        return f"Error getting schema: {str(e)}"

# Define a tool to get longest overdue customer
@mcp.tool()
def get_longest_overdue_customer() -> str:
    """Get customer with longest overdue premium"""
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        
        # Get customer with longest overdue date (earliest due date)
        query = """
            SELECT * FROM policy_info
            WHERE status = 'Discontinuance' OR status = 'overdue' OR outstanding_amount > 0
            ORDER BY date(premium_due_date) ASC 
            LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            # Get column names
            column_names = [description[0] for description in cursor.description]
            # Convert to dictionary
            customer_data = dict(zip(column_names, result))
            conn.close()
            return json.dumps(customer_data, default=str)
        else:
            conn.close()
            return json.dumps({"error": "No overdue customers found"})
            
    except Exception as e:
        conn.close()
        return json.dumps({"error": f"Database query error: {str(e)}"})

# Define a tool to get customer by policy number
@mcp.tool()
def get_customer_by_policy(policy_number: str) -> str:
    """Get customer data by policy number"""
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM policy_info WHERE policy_number = ?"
        cursor.execute(query, (policy_number,))
        result = cursor.fetchone()
        
        if result:
            column_names = [description[0] for description in cursor.description]
            customer_data = dict(zip(column_names, result))
            conn.close()
            return json.dumps(customer_data, default=str)
        else:
            conn.close()
            return json.dumps({"error": f"No customer found with policy number: {policy_number}"})
            
    except Exception as e:
        conn.close()
        return json.dumps({"error": f"Database query error: {str(e)}"})

# Define a tool to get all overdue customers
@mcp.tool()
def get_all_overdue_customers() -> str:
    """Get all customers with overdue premiums"""
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM policy_info
            WHERE status = 'Discontinuance' OR status = 'overdue' OR outstanding_amount > 0
            ORDER BY date(premium_due_date) ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            column_names = [description[0] for description in cursor.description]
            customers = []
            for result in results:
                customer_data = dict(zip(column_names, result))
                customers.append(customer_data)
            conn.close()
            return json.dumps(customers, default=str)
        else:
            conn.close()
            return json.dumps([])
            
    except Exception as e:
        conn.close()
        return json.dumps({"error": f"Database query error: {str(e)}"})

# Define a tool for custom SQL queries (with safety checks)
@mcp.tool()
def execute_safe_query(sql: str) -> str:
    """Execute safe SQL queries (SELECT only)"""
    # Basic safety check - only allow SELECT statements
    if not sql.strip().upper().startswith('SELECT'):
        return json.dumps({"error": "Only SELECT queries are allowed for security"})
    
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if results:
            column_names = [description[0] for description in cursor.description]
            if len(results) == 1:
                # Single result - return as dict
                result_data = dict(zip(column_names, results[0]))
                conn.close()
                return json.dumps(result_data, default=str)
            else:
                # Multiple results - return as list of dicts
                result_list = []
                for result in results:
                    result_data = dict(zip(column_names, result))
                    result_list.append(result_data)
                conn.close()
                return json.dumps(result_list, default=str)
        else:
            conn.close()
            return json.dumps([])
            
    except Exception as e:
        conn.close()
        return json.dumps({"error": f"SQL execution error: {str(e)}"})

# Define a prompt for customer analysis
@mcp.prompt()
def analyze_customer_data(policy_number: str = "") -> List[Dict[str, Any]]:
    """Create a prompt template for analyzing customer data"""
    return [
        {
            "role": "user",
            "content": f"""Please analyze this customer's insurance policy data:
Policy Number: {policy_number}

Database Schema:
{get_schema()}

Provide insights about:
1. Policy status and risk level
2. Payment history and patterns  
3. Recommended actions for customer retention
4. Script customization suggestions
"""
        }
    ]

# Run the MCP server
if __name__ == "__main__":
    print("🚀 Starting Insurance Database MCP Server...")
    print(f"📊 Database: {DB_PATH}")
    print("🔧 Available tools:")
    print("   - get_longest_overdue_customer")
    print("   - get_customer_by_policy") 
    print("   - get_all_overdue_customers")
    print("   - execute_safe_query")
    print("📋 Available resources:")
    print("   - schema://insurance")
    print("💡 Available prompts:")
    print("   - analyze_customer_data")
    print("=" * 50)
    
    mcp.run()
