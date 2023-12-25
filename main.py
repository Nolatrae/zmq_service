import zmq
import sqlite3
import time
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_NAME = 'sensor_data.db'
SERVER_ADDRESS = "tcp://192.168.0.102:5555"
TABLES = {
    'p': 'photoresistor_data',
    't': 'button_data',
    'm': 'gercon_data'
}

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

def setup_database():
    for sensor_type, table_name in TABLES.items():
        if sensor_type == 'p':
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT (datetime('now', 'utc'))
                )
            ''')
        else:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT (datetime('now', 'utc'))
                )
            ''')

    conn.commit()

def process_message(message):
    try:
        if message and len(message) > 0:
            sensor_type = message[0].lower()
            if sensor_type == 'p':
                value = int(message[1:])
            elif sensor_type == 'm' or sensor_type == 't':
                value = sensor_type

            table_name = TABLES.get(sensor_type)
            if table_name:
                if sensor_type == 'p':
                    cursor.execute(f'INSERT INTO {table_name} (value) VALUES (?)', (value,))
                else:
                    cursor.execute(f'INSERT INTO {table_name} DEFAULT VALUES')
            else:
                logger.warning(f"Unknown sensor type: {sensor_type}")
                print(f"Unknown sensor type: {sensor_type}")

            conn.commit()
        else:
            logger.warning("Received empty message or message of insufficient length.")
            print("Received empty message or message of insufficient length.")

    except (zmq.ZMQError, ValueError) as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def main():
    try:
        logger.info("Program startup.")
        print("Program startup.")
        setup_database()

        context = zmq.Context()
        client = context.socket(zmq.SUB)
        client.connect(SERVER_ADDRESS)
        client.subscribe('')

        while True:
            try:
                message = client.recv_string()
                process_message(message)

            except zmq.ZMQError as e:
                logger.error(f"ZMQ Error: {e}")
                logger.info("Attempting to reconnect in 1 second...")
                print(f"ZMQ Error: {e}")
                print("Attempting to reconnect in 1 second...")
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted. Exiting the program.")

if __name__ == "__main__":
    main()

conn.close()
