import sqlite3
import pandas as pd

def crear_tabla():
    conn = sqlite3.connect("llaves.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            area TEXT,
            salon TEXT,
            accion TEXT,
            fecha_hora TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_evento(nombre, area, salon, accion, fecha_hora):
    conn = sqlite3.connect("data/llaves.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO llaves (nombre, area, salon, accion, fecha_hora) VALUES (?, ?, ?, ?, ?)",
                   (nombre, area, salon, accion, fecha_hora))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect("data/llaves.db")
    df = pd.read_sql_query("SELECT * FROM llaves ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df
