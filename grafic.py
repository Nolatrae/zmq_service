import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def plot_sensor_data(table_name, sensor_name, ax=None):
    conn = sqlite3.connect('sensor_data.db')

    columns_query = f"PRAGMA table_info({table_name})"
    columns_info = pd.read_sql_query(columns_query, conn)
    select_columns = ', '.join(columns_info['name'])

    query = f"SELECT {select_columns} FROM {table_name}"
    df = pd.read_sql_query(query, conn)

    conn.close()

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    if 'timestamp' in df.columns:
        df.set_index('timestamp', inplace=True)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    if 'value' in df.columns:
        ax.plot(df.index, df['value'], label=sensor_name)
    else:
        ax.plot(df.index, [1] * len(df), label=sensor_name, marker='o', linestyle='None')
    ax.set_ylabel('Значение' if 'value' in df.columns else 'События')
    ax.set_title(f'График {"" if "value" in df.columns else "событий "} {sensor_name}')
    ax.legend()

fig, axs = plt.subplots(3, 1, figsize=(10, 18))

plot_sensor_data('photoresistor_data', 'Фоторезистор', ax=axs[0], )
plot_sensor_data('button_data', 'Кнопка', ax=axs[1])
plot_sensor_data('gercon_data', 'Геркон', ax=axs[2])

plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.4)

plt.show()
