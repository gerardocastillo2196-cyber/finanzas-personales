import psycopg2
from datetime import datetime

# CONFIGURACIÓN (Tus credenciales)
DB_CONFIG = {
    "dbname": "gastos_db",
    "user": "gerardo_dev",
    "password": "admin123",
    "host": "localhost",
    "port": "5432",
}


def conectar():
    """Abre la puerta de la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error conectando a Postgres: {e}")
        return None


def inicializar_tabla():
    """Crea la tabla de gastos si es la primera vez que corremos la app"""
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()

        sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            categoria VARCHAR(50),
            concepto TEXT,
            monto DECIMAL(10, 2),
            tipo VARCHAR(20),
            metodo_pago VARCHAR (50),
            comision_retiro DECIMAL(5, 2)
        );
        """
        cursor.execute(sql_crear_tabla)

        sql_crear_tabla_tarjetas = """
        CREATE TABLE IF NOT EXISTS tarjetas (
            id SERIAL PRIMARY KEY,
            nombre_tarjeta VARCHAR(50) UNIQUE,
            dia_corte INTEGER,
            dia_pago INTEGER,
            limite DECIMAL(10, 2),
            deuda_actual DECIMAL(10, 2) DEFAULT 0,  
            tasa_interes DECIMAL(5, 2) DEFAULT 0,
            comision_retiro DECIMAL(5,2) DEFAULT 0
        );
        """

        cursor.execute(sql_crear_tabla_tarjetas)

        sql_crear_tabla_debito = """
        CREATE TABLE IF NOT EXISTS cuentas_debito (
            id SERIAL PRIMARY KEY,
            nombre_banco VARCHAR (50) UNIQUE,
            saldo_inicial DECIMAL(10,2) DEFAULT 0
        );
        """

        cursor.execute(sql_crear_tabla_debito)

        sql_crear_tabla_ahorros = """
        CREATE TABLE IF NOT EXISTS cuentas_ahorros (
        id SERIAL PRIMARY KEY,
        nombre_banco VARCHAR (50) UNIQUE,
        saldo_actual DECIMAL(10,2) DEFAULT 0
        );
        """
        cursor.execute(sql_crear_tabla_ahorros)

        cursor.execute(sql_crear_tabla)
        conexion.commit()  # ¡Guardar cambios! Importante en BD
        print("Tablas 'gastos' & 'Tarjetas' verificadas correctamente.")

        cursor.close()
        conexion.close()


# Si ejecutas este archivo, se crea la tabla
if __name__ == "__main__":
    inicializar_tabla()
