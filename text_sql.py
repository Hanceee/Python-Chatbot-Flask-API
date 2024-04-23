import pandas as pd
import pymysql
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Database connection settings
db_host = '127.0.0.1'
db_user = 'root'
db_password = ''
db_name = 'shesh'

# Function to fetch data from the database and write to a text file
def update_text_file():
    # Connect to the database
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    
    # SQL query to fetch data from chatbot_configurations table
    config_sql_query = "SELECT txt_file FROM chatbot_configurations WHERE id = 1"
    
    # Fetch data into a DataFrame
    config_df = pd.read_sql(config_sql_query, conn)
    
    # SQL query to fetch data from lawyers table
    lawyers_sql_query = "SELECT * FROM lawyers"
    
    # Fetch data into a DataFrame
    lawyers_df = pd.read_sql(lawyers_sql_query, conn)
    
    # Combine both DataFrames
    result_df = pd.concat([config_df, lawyers_df], axis=0)
    
    # Format lawyer data
    lawyer_details = []
    for index, row in lawyers_df.iterrows():
        lawyer_detail = f"{index + 1}.  {row['name']}\n"
        lawyer_detail += f"  Contact: {row['contact']}\n"
        lawyer_detail += f"  Specializations: {row['specializations']}\n"
        lawyer_detail += f"  Location: {row['location']}\n"
        lawyer_detail += f"  Experience: {row['experience']} years\n"
        lawyer_details.append(lawyer_detail)
    
    # Join lawyer details
    lawyer_details_str = "\n".join(lawyer_details)
    
    # Write combined data to text file
    with open('familycode.txt', 'w') as file:
        file.write(config_df['txt_file'].iloc[0] + '\n\n')
        file.write("FILIPINO LAWYER CONTACT DETAILS:\n\n")
        file.write(lawyer_details_str)
    
    # Close the database connection
    conn.close()

# Class to handle file system events
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        update_text_file()
        print("Text file updated")

# Continuous update loop
while True:
    update_text_file()
    print("Text file updated")
    sleep(10)  # Update every 10 seconds

# Watchdog setup
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

