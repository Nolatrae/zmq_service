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
    'b': 'button_data',
    'g': 'gercon_data'
}

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

def setup_database():
    for table_name in TABLES.values():
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()

def process_message(message):
    try:
        if message and len(message) > 1:
            sensor_type = message[0].lower()
            value = int(message[1:])
            print(value)

            table_name = TABLES.get(sensor_type)
            if table_name:
                cursor.execute(f'INSERT INTO {table_name} (value) VALUES (?)', (value,))
            else:
                logger.warning(f"Неизвестный тип датчика: {sensor_type}")
                print(f"Неизвестный тип датчика: {sensor_type}")

            conn.commit()
        else:
            logger.warning("Получено пустое сообщение или сообщение недостаточной длины.")
            print("Получено пустое сообщение или сообщение недостаточной длины.")

    except (zmq.ZMQError, ValueError) as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")

def main():
    try:
        logger.info("Запуск программы.")
        print("Запуск программы.")
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
                logger.error(f"Произошла ошибка ZMQ: {e}")
                logger.info("Попытка переподключения через 1 секунду...")
                print(f"Произошла ошибка ZMQ: {e}")
                print("Попытка переподключения через 1 секунду...")
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Прервано. Завершаем программу.")

if __name__ == "__main__":
    main()

conn.close()
