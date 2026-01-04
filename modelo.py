from base_datos import conectar
import pandas as pd
from datetime import datetime, timedelta
from base_datos import inicializar_tabla


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

    def guardar_movimientos_tarjeta(
        self, nombre, corte, pago, limite, deuda_inicial, interes, comision
    ):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO tarjetas (nombre_tarjeta , dia_corte, dia_pago,limite, deuda_actual, tasa_interes,comision_retiro) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                valores = (
                    nombre,
                    corte,
                    pago,
                    limite,
                    deuda_inicial,
                    interes,
                    comision,
                )
                cursor.execute(sql, valores)
                conexion.commit()
                return True
            except Exception as e:
                print(f"ERROR al guardar esta tarjeta: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()

    def obtener_estado_credito(self):
        conexion = conectar()
        datos_estado = []
        if conexion:
            try:
                cursor = conexion.cursor()
                sql_tarjetas = "SELECT nombre_tarjeta,limite,deuda_actual, comision_retiro FROM tarjetas"
                cursor.execute(sql_tarjetas)
                tarjetas = cursor.fetchall()

                for tarjeta in tarjetas:
                    nombre = tarjeta[0]
                    limite = float(tarjeta[1])
                    deuda_inicial = float(tarjeta[2])
                    tasa_comision = float(tarjeta[3])

                    # Suma Gasto
                    sql_gasto = "SELECT SUM(monto) FROM gastos WHERE metodo_pago = %s AND tipo = 'GASTO'"
                    cursor.execute(sql_gasto, (nombre,))
                    resultado = cursor.fetchone()

                    total_gastos = float(resultado[0]) if resultado[0] else 0.0

                    # Suma Retiros
                    sql_retiro = "SELECT SUM(monto) FROM gastos WHERE metodo_pago = %s AND tipo = 'RETIRO'"
                    cursor.execute(sql_retiro, (nombre,))
                    res_retiro = cursor.fetchone()
                    monto_retiros = float(res_retiro[0]) if res_retiro[0] else 0.0

                    total_retiros = monto_retiros + (
                        monto_retiros * (tasa_comision / 100)
                    )

                    # Restar Abonos
                    sql_abono = "SELECT SUM(monto) FROM gastos WHERE metodo_pago = %s AND tipo = 'ABONO A TARJETA'"
                    cursor.execute(sql_abono, (nombre,))
                    res_abono = cursor.fetchone()
                    total_abonos = float(res_abono[0]) if res_abono[0] else 0.0

                    gasto_total = (
                        deuda_inicial + total_gastos + total_retiros - total_abonos
                    )

                    datos_estado.append((nombre, gasto_total, limite))

                    print(f"--- DIAGNÓSTICO PARA {nombre} ---")
                    print(f"Base: {deuda_inicial} | Gastos: {total_gastos}")
                    print(
                        f"Retiros (+comisión): {total_retiros} | Pagos: {total_abonos}"
                    )
                    print(f"Total Final: {gasto_total}")
                    print("-----------------------------------")
                    print("-----------------------------------")

            except Exception as e:
                print(f"Error calculando crédito: {e}")
            finally:
                cursor.close()
                conexion.close()

        return datos_estado

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
                sql_tarjetas = "SELECT nombre_tarjeta FROM tarjetas"
                cursor.execute(sql_tarjetas)
                lista_credito = [fila[0] for fila in cursor.fetchall()]
                lista_credito.append("TARJETA DE CREDITO")

                sql = """SELECT tipo, metodo_pago, SUM(monto)
                        FROM gastos
                        GROUP BY tipo, metodo_pago"""

                cursor.execute(sql)
                datos = cursor.fetchall()

                total_salida_liquidas = 0
                total_ingresos = 0

                for fila in datos:
                    tipo = fila[0]
                    metodo = fila[1]
                    monto = float(fila[2])

                    if tipo == "INGRESO":
                        total_ingresos += monto

                    elif tipo == "RETIRO":
                        if metodo in lista_credito:
                            total_ingresos += monto

                    elif tipo == "ABONO A TARJETA":
                        total_salida_liquidas += monto

                    elif tipo == "AHORROS":
                        total_salida_liquidas += monto

                    elif tipo == "GASTO":
                        if metodo not in lista_credito:
                            total_salida_liquidas += monto

                balance_final = total_ingresos - total_salida_liquidas

            except Exception as e:
                print(f"ERROR al calcular balance: {e}")

            finally:
                cursor.close()
                conexion.close()

        return balance_final

    def resetear_base_datos(self):
        conexion = conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql_gastos = "DROP TABLE gastos CASCADE;"
                cursor.execute(sql_gastos)
                sql_tarjetas = "DROP TABLE tarjetas CASCADE;"
                cursor.execute(sql_tarjetas)
                conexion.commit()
                print("Tablas eliminadas. Se recrearán al reiniciar la app.")
                inicializar_tabla()
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

    def obtener_proyeccion_pagos(self):
        conexion = conectar()
        proyecciones = {}

        if conexion:
            try:
                cursor = conexion.cursor()

                sql = "SELECT fecha, monto, metodo_pago FROM gastos WHERE tipo='GASTO'"
                cursor.execute(sql)
                gastos = cursor.fetchall()

                for gasto in gastos:
                    fecha_compra = gasto[0]
                    monto = float(gasto[1])
                    nombre_tarjeta = gasto[2]

                    reglas = self.obtener_datos_tarjeta(nombre_tarjeta)

                    if reglas:
                        dia_corte = reglas[0]
                        dia_pago = reglas[1]
                        try:
                            fecha_pago_estimada = fecha_compra.replace(day=dia_pago)
                        except ValueError:
                            fecha_pago_estimada = fecha_compra.replace(day=28)

                        if fecha_compra.day > dia_corte:
                            fecha_pago_estimada = fecha_compra + timedelta(days=30)
                            try:
                                fecha_pago_estimada = fecha_compra.replace(day=dia_pago)
                            except ValueError:
                                fecha_pago_estimada = fecha_compra + timedelta(days=28)

                        if fecha_pago_estimada < fecha_compra:
                            fecha_pago_estimada = fecha_compra + timedelta(days=30)
                            try:
                                fecha_pago_estimada = fecha_compra.replace(day=dia_pago)
                            except:
                                pass

                        clave_fecha = fecha_pago_estimada.strftime("%Y-%m-%d")

                        if clave_fecha in proyecciones:
                            proyecciones[clave_fecha] += monto
                        else:
                            proyecciones[clave_fecha] = monto

            except Exception as e:
                print(f"ERROR en el calculo de proyecciones: {e}")
            finally:
                conexion.close()

        return list(proyecciones.items())

    def obtener_todos_los_gastos(self):
        conexion = conectar()
        lista_gastos = []

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT id, fecha, categoria,concepto,monto,tipo,metodo_pago FROM gastos ORDER BY fecha DESC"
                cursor.execute(sql)
                lista_gastos = cursor.fetchall()
            except Exception as e:
                print(f"ERROR al obtener datos de los gastos: {e}")
            finally:
                cursor.close()
                conexion.close()

        return lista_gastos

    def obtener_gasto_por_id(
        self,
        id_gasto,
    ):
        conexion = conectar()
        dato = None
        cursor = None
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT categoria, concepto, monto,metodo_pago FROM gastos WHERE id = %s"
                cursor.execute(sql, (id_gasto,))
                dato = cursor.fetchone()
            except Exception as e:
                print(f"ERROR al obtener el gasto {e}")
            finally:
                if cursor:
                    cursor.close()
                conexion.close()
        return dato

    def actualizar_gasto(
        self,
        id_gasto,
        nueva_cat,
        nuevo_concepto,
        nuevo_monto,
        metodo_pago,
    ):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """
                    UPDATE gastos
                    SET categoria=%s, concepto=%s, monto=%s, metodo_pago=%s
                    WHERE id = %s
                    """
                valores = (
                    nueva_cat,
                    nuevo_concepto,
                    nuevo_monto,
                    metodo_pago,
                    id_gasto,
                )
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Gasto {id_gasto} actualizado exitosamente")
                return True
            except Exception as e:
                print(f"Error al actualizar el gasto {id_gasto}: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()

    def eliminar_gasto(self, id_gasto):
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "DELETE FROM gastos WHERE id = %s"
                cursor.execute(sql, (id_gasto,))
                conexion.commit()
                print(f"Gasto {id_gasto} eliminado")
                return True
            except Exception as e:
                print(f"Error al eliminar gasto: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
