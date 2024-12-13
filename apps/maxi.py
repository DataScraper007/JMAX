import os
import re
import pandas as pd
from datetime import datetime
import pymysql  # Replace with your DB library

def maxi_count(start_date, end_date):
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "actowiz",
        "database": "maxi_ca"
    }

    try:
        # Parse the date range
        start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
        end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

        # Connect to the database
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Query to fetch all tables in the database
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        # Regex to match table names with date pattern
        table_pattern = re.compile(r"maxi_ca_products_(\d{8})")

        # Collect counts for tables within the date range
        results = []
        for table in tables:
            match = table_pattern.match(table)
            if match:
                table_date = datetime.strptime(match.group(1), "%Y%m%d")
                if start_date_obj <= table_date <= end_date_obj:
                    # Count the records in the table
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        results.append({"date": table_date.strftime("%Y-%m-%d"), "count": count})
                    except Exception as e:
                        return {"status": "error", "status_code": 500, "message": f"Error counting records in table {table}: {str(e)}"}

        # Close the database connection
        cursor.close()
        conn.close()

        # Prepare the output directory and file
        os.makedirs('./files/maxi_count', exist_ok=True)
        output_file = f"files/maxi_count/maxi_count_{start_date}_{end_date}.xlsx"

        # Convert results to a DataFrame and save to Excel
        df = pd.DataFrame(results)
        if not df.empty:
            df.sort_values(by="date", inplace=True)  # Sort by date
            df.to_excel(output_file, index=False)
            return {"status": "success", "status_code": 200, "message": "Data processed successfully", "file": output_file}
        else:
            return {"status": "success", "status_code": 204, "message": "No data found for the given date range", "file": None}

    except pymysql.Error as db_err:
        return {"status": "error", "status_code": 500, "message": f"Database error: {str(db_err)}"}
    except ValueError as date_err:
        return {"status": "error", "status_code": 400, "message": f"Date parsing error: {str(date_err)}"}
    except Exception as gen_err:
        return {"status": "error", "status_code": 500, "message": f"Unexpected error: {str(gen_err)}"}
