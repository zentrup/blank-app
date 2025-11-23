import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime

# Database connection
def get_db_connection():
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=gfau-ext-sql01.database.windows.net;"
        "Database=GFAUEXT_TEST;"
        "UID=GFL_MET_ReadWrite;"
        "PWD=Sklen4Ba!kjks;"
    )
    conn = pyodbc.connect(conn_str)
    return conn

# Query to get the last update time from each table using the 'date' column
def get_last_update_times_by_site():
    conn = get_db_connection()
    
    # Define all the tables (Shift, Day, and Month)
    shift_tables = [
        'AGM_Shift_Actual', 'CC_Shift_Actual', 'DA_Shift_Actual', 
        'GGM_Shift_Actual', 'GSM_Shift_Actual', 'SD_Shift_Actual',
        'SGM_Shift_Actual', 'SN_Shift_Actual', 'TK_Shift_Actual'
    ]
    
    day_tables = [
        'AGM_Day_Actual', 'CC_Day_Actual', 'DA_Day_Actual', 
        'GGM_Day_Actual', 'GSM_Day_Actual', 'SD_Day_Actual',
        'SGM_Day_Actual', 'SN_Day_Actual', 'TK_Day_Actual'
    ]
    
    month_tables = [
        'AGM_Month_Actual', 'CC_Month_Actual', 'DA_Month_Actual',
        'GGM_Month_Actual', 'GSM_Month_Actual', 'SD_Month_Actual',
        'SGM_Month_Actual', 'SN_Month_Actual', 'TK_Month_Actual'
    ]
    
    # All tables combined
    all_tables = shift_tables + day_tables + month_tables
    
    # Dictionary to store last update times, organized by site
    site_data = {}
    
    for table in all_tables:
        # Extract the site acronym by splitting the table name at the underscore and taking the first part
        site = table.split('_')[0]
        
        # Query to retrieve the most recent 'date' for each site from each table
        query = f"""
        SELECT MAX([date]) as last_update
        FROM metmonthly.{table};
        """
        df = pd.read_sql(query, conn)
        
        # If we have data for this table, add it to the site_data dictionary
        if not df.empty:
            last_update = df.iloc[0]['last_update']
            if site not in site_data:
                site_data[site] = {}
            site_data[site][table] = last_update
        else:
            # Ensure that if there is no data for a table, we set last_update as None
            if site not in site_data:
                site_data[site] = {}
            site_data[site][table] = None
    
    conn.close()
    return site_data

# Function to categorize times based on the given thresholds
def categorize_time(last_update, table_type):
    if last_update is None:
        return "blue"  # Blue if no data
        
    now = datetime.now()
    time_diff = now - last_update
    hours_diff = time_diff.total_seconds() / 3600
    days_diff = time_diff.total_seconds() / (3600 * 24)

    # Define thresholds for each table type
    if table_type == 'shift':
        if hours_diff <= 12:
            return "green"
        elif hours_diff <= 24:
            return "yellow"
        else:
            return "red"
    elif table_type == 'day':
        if hours_diff <= 24:
            return "green"
        elif hours_diff <= 32:
            return "yellow"
        else:
            return "red"
    elif table_type == 'month':
        if days_diff <= 60:
            return "green"
        elif days_diff <= 63:
            return "yellow"
        else:
            return "red"
# Function to display the Kanban board with colored boxes
def create_kanban_board():
    st.title("Shift, Day, and Month Tables Kanban Matrix")

    site_data = get_last_update_times_by_site()

    shift_tables = [
        'AGM_Shift_Actual','CC_Shift_Actual','DA_Shift_Actual',
        'GGM_Shift_Actual','GSM_Shift_Actual','SD_Shift_Actual',
        'SGM_Shift_Actual','SN_Shift_Actual','TK_Shift_Actual'
    ]
    day_tables = [
        'AGM_Day_Actual','CC_Day_Actual','DA_Day_Actual',
        'GGM_Day_Actual','GSM_Day_Actual','SD_Day_Actual',
        'SGM_Day_Actual','SN_Day_Actual','TK_Day_Actual'
    ]
    month_tables = [
        'AGM_Month_Actual','CC_Month_Actual','DA_Month_Actual',
        'GGM_Month_Actual','GSM_Month_Actual','SD_Month_Actual',
        'SGM_Month_Actual','SN_Month_Actual','TK_Month_Actual'
    ]

    columns = st.columns([3, 3, 3])

    # SHIFT COLUMN
    with columns[0]:
        st.subheader("Shift")
        for site in site_data.keys():
            st.write(f"**{site}**")

            # Collect timestamps from all shift tables for this site
            timestamps = [
                site_data[site].get(tbl) for tbl in shift_tables
                if site_data[site].get(tbl) is not None
            ]
            
            # Determine color
            if not timestamps:
                color = "blue"
                label = "No Data"
            else:
                newest = max(timestamps)
                color = categorize_time(newest, "shift")
                label = newest

            st.markdown(f"""
            <div style="background-color:{color}; padding:6px; 
                margin-bottom:5px; border-radius:5px;">
                <strong>{label}</strong>
            </div>
            """, unsafe_allow_html=True)

    # DAY COLUMN
    with columns[1]:
        st.subheader("Day")
        for site in site_data.keys():
            st.write(f"**{site}**")

            timestamps = [
                site_data[site].get(tbl) for tbl in day_tables
                if site_data[site].get(tbl) is not None
            ]
            
            if not timestamps:
                color = "blue"
                label = "No Data"
            else:
                newest = max(timestamps)
                color = categorize_time(newest, "day")
                label = newest

            st.markdown(f"""
            <div style="background-color:{color}; padding:6px; 
                margin-bottom:5px; border-radius:5px;">
                <strong>{label}</strong>
            </div>
            """, unsafe_allow_html=True)

    # MONTH COLUMN
    with columns[2]:
        st.subheader("Month")
        for site in site_data.keys():
            st.write(f"**{site}**")

            timestamps = [
                site_data[site].get(tbl) for tbl in month_tables
                if site_data[site].get(tbl) is not None
            ]
            
            if not timestamps:
                color = "blue"
                label = "No Data"
            else:
                newest = max(timestamps)
                color = categorize_time(newest, "month")
                label = newest

            st.markdown(f"""
            <div style="background-color:{color}; padding:6px; 
                margin-bottom:5px; border-radius:5px;">
                <strong>{label}</strong>
            </div>
            """, unsafe_allow_html=True)
if __name__ == "__main__":
    create_kanban_board()
