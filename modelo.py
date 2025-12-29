from base_datos import conectar
import pandas as pd
from datetime import datetime, timedelta


class GestorGastos:

    def __init__(self):
        pass

    def guardar_gastos(self, categoria, concepto, monto, tipo, metodo_pago):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()

                sql = "INSERT INTO gastos (categoria, concepto, monto, tipo, metodo_pago) VALUES (%s,%s,%s,%s,%s)"
                valores = (categoria, concepto, monto, tipo, metodo_pago)

                cursor.execute(sql, valores)
                conexion.commit()
                print(f"movimiento guardado: {tipo} -Q{metodo_pago}")
            except Exception as e:
                print(f"ERROR AL GUARDAR! {e}")

            finally:
                cursor.close()
                conexion.close()

    def guardar_movimientos_tarjeta(self, nombre, corte, pago):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO tarjetas (nombre_tarjeta , dia_corte, dia_pago) VALUES (%s, %s, %s)"
                valores = (nombre, corte, pago)
                cursor.execute(sql, valores)
                conexion.commit()
                return True
            except Exception as e:
                print("ERROR al guardar esta tarjeta")
                return False
            finally:
                cursor.close()
                conexion.close()

    def obtener_gastos_por_categoria(self):
        conexion = conectar()
        resultados = []
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """SELECT tipo || '-' || categoria, SUM(monto)
                        FROM gastos
                        GROUP BY tipo, categoria

                        """
                cursor.execute(sql)
                resultados = cursor.fetchall()
            except Exception as e:
                print("ERROR al analizar los datos")
            finally:
                cursor.close()
                conexion.close()
        return resultados

    def calcular_balance(self):
        conexion = conectar()
        balance_final = 0

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """SELECT tipo, SUM(monto)
                        FROM gastos
                        GROUP BY tipo"""

                cursor.execute(sql)
                datos = cursor.fetchall()

                totales = {"INGRESO": 0, "GASTO": 0, "AHORROS": 0}

                for fila in datos:
                    nombre_tipo = fila[0]
                    suma = fila[1]

                    if nombre_tipo in totales:
                        totales[nombre_tipo] = suma

                balance_final = totales["INGRESO"] - (
                    totales["GASTO"] + totales["AHORROS"]
                )
            except Exception as e:
                print(f"Error al calcular su balance: {e}")

            finally:
                cursor.close()
                conexion.close()

        return balance_final

    def resetear_base_datos(self):
        conexion = conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql_gastos = "TRUNCATE TABLE gastos RESTART IDENTITY CASCADE;"
                cursor.execute(sql_gastos)
                sql_tarjetas = "TRUNCATE TABLE tarjetas RESTART IDENTITY CASCADE;"
                cursor.execute(sql_tarjetas)
                conexion.commit()
                print("Bases de datos reseteadas al 100%")
                return True
            except Exception as e:
                print(f"Error al resetear las bases de datos. {e}")
                return False
            finally:
                cursor.close()
                conexion.close()

    def exportar_excel(self, ruta_archivo):
        conexion = conectar()
        if conexion:
            try:
                sql = "SELECT id, fecha, tipo, categoria, concepto, monto, metodo_pago FROM gastos ORDER BY fecha DESC"
                df = pd.read_sql_query(sql, conexion)
                df.to_excel(ruta_archivo, index=False)

                print(f"Excel guardado en: {ruta_archivo}")
                return True
            except Exception as e:
                print(f"Error al Exportar su reporte: {e}")
                return False
            finally:
                conexion.close()

    def obtener_nombre_tarjetas(self):
        conexion = conectar()
        lista_nombres = []
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT nombre_tarjeta FROM tarjetas"
                cursor.execute(sql)
                datos = cursor.fetchall()

                for fila in datos:
                    lista_nombres.append(fila[0])
            except Exception as e:
                print(f"Erro al obtener tarjeta {e}")
            finally:
                cursor.close()
                conexion.close()

        return lista_nombres

    def obtener_datos_tarjeta(self, nombre_tarjeta):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = (
                    "SELECT dia_corte, dia_pago FROM tarjetas WHERE nombre_tarjeta = %s"
                )
                cursor.execute(sql, (nombre_tarjeta,))
                resultado = cursor.fetchone()
                return resultado
            except Exception as e:
                print(f"Error al obtener datos de la tarjeta {e}")
            finally:
                cursor.close()
                conexion.close()
        return None

    # ESTA ES LA FUNCIÓN QUE TE FALTA EN MODELO.PY
    def obtener_proyeccion_pagos(self):
        conexion = conectar()
        proyecciones = {}

        if conexion:
            try:
                cursor = conexion.cursor()
                # 1. Traemos fecha, monto y el nombre de la tarjeta (metodo_pago)
                sql = (
                    "SELECT fecha, monto, metodo_pago FROM gastos WHERE tipo = 'GASTO'"
                )
                cursor.execute(sql)
                gastos = cursor.fetchall()

                for gasto in gastos:
                    fecha_compra = gasto[0]
                    monto = float(gasto[1])
                    nombre_tarjeta = gasto[2]

                    # 2. Usamos la función que YA tienes: obtener_datos_tarjeta
                    reglas = self.obtener_datos_tarjeta(nombre_tarjeta)

                    if reglas:
                        dia_corte = reglas[0]
                        dia_pago = reglas[1]

                        # --- CÁLCULO DE FECHAS ---
                        # Creamos fecha tentativa con el día de pago de este mes
                        fecha_pago_estimada = fecha_compra.replace(day=dia_pago)

                        # Si compré DESPUÉS del corte, pago el otro mes
                        if fecha_compra.day > dia_corte:
                            fecha_pago_estimada = fecha_pago_estimada + timedelta(
                                days=30
                            )
                            # Ajustar al día exacto
                            try:
                                fecha_pago_estimada = fecha_pago_estimada.replace(
                                    day=dia_pago
                                )
                            except ValueError:
                                # Caso especial: Febrero o meses de 30 días
                                # Si el día de pago es 31 y el mes no tiene, pasamos al 1 del sig mes
                                fecha_pago_estimada = fecha_pago_estimada + timedelta(
                                    days=1
                                )
                                fecha_pago_estimada = fecha_pago_estimada.replace(day=1)

                        # Si la fecha estimada ya pasó, sumamos un mes
                        if fecha_pago_estimada < fecha_compra:
                            fecha_pago_estimada = fecha_pago_estimada + timedelta(
                                days=30
                            )
                            try:
                                fecha_pago_estimada = fecha_pago_estimada.replace(
                                    day=dia_pago
                                )
                            except:
                                fecha_pago_estimada = fecha_pago_estimada.replace(
                                    day=28
                                )  # Parche simple

                        clave_fecha = fecha_pago_estimada.strftime("%Y-%m-%d")

                        if clave_fecha in proyecciones:
                            proyecciones[clave_fecha] += monto
                        else:
                            proyecciones[clave_fecha] = monto

            except Exception as e:
                print(f"Error calculando proyecciones: {e}")
            finally:
                conexion.close()

        return list(proyecciones.items())
