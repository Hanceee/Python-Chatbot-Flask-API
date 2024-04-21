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
    
    # SQL query to fetch data
    sql_query = "SELECT txt_file FROM chatbot_configurations WHERE id = 1"
    
    # Fetch data into a DataFrame
    df = pd.read_sql(sql_query, conn)
    
    # Write DataFrame to text file
    df.to_csv('familycode.txt', index=False, header=False)
    
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