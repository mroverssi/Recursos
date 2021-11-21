#!/usr/bin/env python
# coding: utf-8

# # ETL


from pyspark.sql import SparkSession
from pyspark.sql import functions
from pyspark.sql.types import StructType
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql.types import FloatType
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf
import numpy as np
from pyspark.sql.functions import isnan, when, count, col
from pyspark.rdd import RDD
import copy
import pandas as pd
from pyspark.sql.functions import row_number, monotonically_increasing_id
from pyspark.sql import Window
from pyspark.sql.functions import regexp_replace
from pyspark.sql.functions import udf, isnan, when, count, col, to_date, regexp_replace, concat_ws, abs
from pyspark.sql import functions as f
from pyspark.sql.functions import monotonically_increasing_id, upper, concat 

import datetime
from pyspark.sql.functions import year, month, dayofmonth


# # Tutorial: creación de ETLs con PySpark



spark_context = SparkContext()
sql_context = SQLContext(spark_context)
spark = sql_context.sparkSession

# Cargar las bases de datos 
dfv = sql_context.read.format("csv").option("header", "true").option("infersSchema", "true").load("vuelosEtapa2.csv")
dfa = sql_context.read.format("csv").option("header", "true").option("infersSchema", "true").load("aeropuertos_cambios_infraestructura.csv")



#Dimension fecha
fecha = dfv.alias("fecha")


#Transformació, dimensión fecha
fecha= fecha.select("ano","mes")



#Eliminar duplicados
fecha=fecha.drop_duplicates()


fecha= fecha.withColumn("mes", fecha["mes"].cast("integer"))


#Ordenar

fecha=fecha.sort("ano","mes")




#Agregar columna key
fecha = fecha.withColumn(
    "fecha_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)



fecha.summary().show()



fecha.head(5)


#Exportar
fecha.toPandas().to_csv('fecha_v2.csv',index=False)



#Dimension empresa
empresa=dfv.alias("empresa")


#Transformación, dimensión empresa
empresa= empresa.select("empresa")




#Eliminar duplicados
empresa=empresa.drop_duplicates()


#Ordenar

empresa=empresa.sort("empresa")


#Agregar columna key
empresa = empresa.withColumn(
    "empresa_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)


#Exportar
empresa.toPandas().to_csv('empresa_v2.csv',index=False)

empresa.summary().show()

empresa.head(5)

#Dimension tipo de vuelo
tipo_de_vuelo = dfv.alias("tipo_de_vuelo")


#Transformación tipo de vuelo
tipo_de_vuelo= tipo_de_vuelo.select("tipo_vuelo")

#Eliminar duplicados
tipo_de_vuelo=tipo_de_vuelo.drop_duplicates()


#Ordenar
tipo_de_vuelo=tipo_de_vuelo.sort("tipo_vuelo")


#Agregar columna key
tipo_de_vuelo = tipo_de_vuelo.withColumn(
    "tipo_de_vuelo_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)

#Exportar
tipo_de_vuelo.toPandas().to_csv('tipo_de_vuelo_v2.csv',index=False)


tipo_de_vuelo.summary().show()

tipo_de_vuelo.head(5)


#Dimension tráfico
trafico = dfv.alias("trafico")

#Transformación tipo de vuelo
trafico= trafico.select("trafico")


#Eliminar duplicados
trafico=trafico.drop_duplicates()

#Sustituir "nan" por "desconocido"
trafico=trafico.withColumn('trafico', regexp_replace('trafico', 'nan', 'desconocido')) 


#Ordenar

trafico=trafico.sort("trafico")

#Agregar columna key
trafico = trafico.withColumn(
    "trafico_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)

#Exportar
trafico.toPandas().to_csv('trafico_v2.csv',index=False)


trafico.summary().show()
trafico.head(5)


#Dimension aeropuertos
df_aeropuertos = dfa.alias("df_aeropuertos")

df_aeropuertos

#Cambiar el tipo de las columnas
df_aeropuertos = df_aeropuertos.withColumn("longitud_pista",df_aeropuertos["longitud_pista"].cast(FloatType()))
df_aeropuertos = df_aeropuertos.withColumn("ancho_pista",df_aeropuertos["ancho_pista"].cast(FloatType()))
df_aeropuertos = df_aeropuertos.withColumn("pbmo",df_aeropuertos["pbmo"].cast(FloatType()))
df_aeropuertos = df_aeropuertos.withColumn("numero_vuelos_origen",df_aeropuertos["numero_vuelos_origen"].cast('int'))
df_aeropuertos = df_aeropuertos.withColumn("gcd_departamento",df_aeropuertos["gcd_departamento"].cast(StringType()))
df_aeropuertos = df_aeropuertos.withColumn("gcd_municipio",df_aeropuertos["gcd_municipio"].cast(StringType()))
df_aeropuertos = df_aeropuertos.withColumn('fecha_construccion',to_date(df_aeropuertos.fecha_construccion, 'yyyy-mm-dd'))
df_aeropuertos = df_aeropuertos.withColumn('fecha_vigencia',to_date(df_aeropuertos.fecha_vigencia, 'yyyy-mm-dd'))
df_aeropuertos = df_aeropuertos.withColumn("resolucion",df_aeropuertos["resolucion"].cast(StringType()))
df_aeropuertos = df_aeropuertos.withColumn("latitud",df_aeropuertos["latitud"].cast(FloatType()))
df_aeropuertos = df_aeropuertos.withColumn("longitud",df_aeropuertos["longitud"].cast(FloatType()))
df_aeropuertos = df_aeropuertos.withColumn("Ano",df_aeropuertos["Ano"].cast(StringType()))


#Eliminar columnas y otros ajustes
df_aeropuertos = df_aeropuertos.fillna({'pbmo': 0, 'resolucion': 0, 'propietario': 0})


#Ordenar por nombres
df_aeropuertos=df_aeropuertos.sort("nombre")


#Agregar columna key
df_aeropuertos = df_aeropuertos.withColumn(
    "aeropuertos_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)



df_aeropuertos = df_aeropuertos.select('aeropuertos_key','iata','sigla','nombre','categoria','clase', 'tipo','municipio',
                                       'departamento','propietario', 'explotador','resolucion','fecha_construccion',
                                       'fecha_vigencia','Ano','latitud','longitud','elevacion','numero_vuelos_origen',
                                       'longitud_pista','ancho_pista','pbmo')


#Copia del dataframe
df2_aeropuertos = df_aeropuertos.alias('df2_aeropuertos')


#Se utiliza un Window para extraer, del dataframe pasado por parámetro #Es decir, por cada llave natural, extrae la última versión.
window = Window.partitionBy(df2_aeropuertos['sigla']).orderBy(df2_aeropuertos['Ano'].desc())
df2_aeropuertos = df2_aeropuertos.select('*', f.rank().over(window).alias('rank')).filter(f.col('rank') == 1) 
df2_aeropuertos = df2_aeropuertos.drop('rank')


#Ajustar nombres en nuevo DF para poder hacer el join con el df original
df2_aeropuertos = df2_aeropuertos.selectExpr('aeropuertos_key','Ano as Ano_2')


#Realiza left join entre df_aeropuertos y df2_aeropuertos
df = df_aeropuertos.join(df2_aeropuertos, how = 'left', on ='aeropuertos_key')


df.show()


#estado_actual = No, registros anteriores de modificación del aerorpuerto
#estado_actual = Si, último registro de modificación del aeropuerto
df = df.withColumn('estado_actual', f.when(df['Ano_2'].isNull(), 'No').otherwise('Si'))
df = df.withColumn('fecha_vigencia_final', f.when(df['estado_actual'] == 'Si', f.to_date(f.lit('2199-12-31'), 'yyyy-MM-dd')).
                   otherwise(f.to_date(concat(col('Ano'),f.lit('-12-31')), 'yyyy-MM-dd')))


# IDENTIFICAR PRIMER REGISTRO PARA ASIGNAR FECHA VIGENCIA INICIAL
#Se utiliza un Window para extraer, del dataframe pasado por parámetro #Es decir, por cada llave natural, extrae la última versión.
df2_aeropuertos = df_aeropuertos.alias('df2_aeropuertos')
window = Window.partitionBy(df2_aeropuertos['sigla']).orderBy(df2_aeropuertos['Ano'].asc())
df2_aeropuertos = df2_aeropuertos.select('*', f.rank().over(window).alias('rank')).filter(f.col('rank') == 1) 
df2_aeropuertos = df2_aeropuertos.drop('rank')



#Ajustar nombres en nuevo DF para poder hacer el join con el df original
df2_aeropuertos = df2_aeropuertos.selectExpr('aeropuertos_key','fecha_construccion as fecha_vigencia_inicial','Ano as Ano_3')
#Realiza left join entre df_aeropuertos y df2_aeropuertos
df = df.join(df2_aeropuertos, how = 'left', on ='aeropuertos_key')



#estado_inicial = No, registros posteriores de modificación del aerorpuerto
#estado_inicial = Si, primer registro de construcción del aeropuerto
df = df.withColumn('estado_inicial', f.when(df['Ano_3'].isNull(), 'No').otherwise('Si'))
df = df.withColumn('fecha_vigencia_inicial', f.when(df['estado_inicial'] == 'Si', df['fecha_construccion']).
                   otherwise(f.to_date(concat(col('Ano'),f.lit('-01-01')), 'yyyy-MM-dd')))



# Seleccionar columnas para archivo csv
df_aeropuertos = df.select('aeropuertos_key','iata','sigla','nombre','categoria','clase','tipo','municipio','departamento',
 'propietario','explotador','resolucion','fecha_construccion','fecha_vigencia','Ano',
          'latitud','longitud','elevacion','numero_vuelos_origen','longitud_pista','ancho_pista','pbmo',
          'estado_actual','fecha_vigencia_inicial','fecha_vigencia_final',year("fecha_vigencia_inicial").alias("ano_inicial"),year("fecha_vigencia_final").alias("ano_final"))


df_aeropuertos.select('nombre','fecha_construccion','Ano','fecha_vigencia_inicial','fecha_vigencia_final',"ano_inicial", "ano_final").show(20)


df_aeropuertos_csv=df_aeropuertos.alias("df_aeropuertos_csv")


df_aeropuertos_csv=df_aeropuertos_csv.drop("ano_inicial","ano_final")


df_aeropuertos_csv.printSchema()


#Exportar
df_aeropuertos_csv.toPandas().to_csv('aeropuertos_v3.csv',index=False)


#Tabla de hechos
fact_vuelos = dfv.alias("fact_vuelos")



#Cambio del tipo de columna
fact_vuelos = fact_vuelos.withColumn("vuelos",fact_vuelos["vuelos"].cast('int'))
fact_vuelos = fact_vuelos.withColumn("sillas",fact_vuelos["sillas"].cast('int'))
fact_vuelos = fact_vuelos.withColumn("pasajeros",fact_vuelos["pasajeros"].cast('int'))
fact_vuelos = fact_vuelos.withColumn("carga_ofrecida",fact_vuelos["carga_ofrecida"].cast(FloatType()))
fact_vuelos = fact_vuelos.withColumn("carga_bordo",fact_vuelos["carga_bordo"].cast(FloatType()))
fact_vuelos = fact_vuelos.withColumn("ano",fact_vuelos["ano"].cast(StringType()))
fact_vuelos = fact_vuelos.withColumn("mes",fact_vuelos["mes"].cast(StringType()))


#
fact_vuelos = fact_vuelos.fillna({'sillas': 0, 'pasajeros': 0})
fact_vuelos = fact_vuelos.withColumn('trafico', regexp_replace('trafico', 'nan', 'N'))



ajuste_mes = {'1':'01', '2':'02', '3':'03', '4':'04', '5':'05', '6':'06', '7':'07', '8':'08', '9':'09'}
fact_vuelos = fact_vuelos.na.replace(ajuste_mes,2,'mes')


#Incluir foreign keys
key_fecha=fecha.alias("fecha")


#Fecha
fact_vuelos = fact_vuelos.join(key_fecha, ["ano","mes"] )


#Empresa
key_empresa=empresa.alias("key_empresa")



fact_vuelos = fact_vuelos.join(key_empresa, ["empresa"] )


#Tipo de vuelo
key_tipo_de_vuelo=tipo_de_vuelo.alias("key_tipo_de_vuelo")




fact_vuelos = fact_vuelos.join(key_tipo_de_vuelo, ["tipo_vuelo"] )




#Trafico
key_trafico=trafico.alias("key_trafico")



fact_vuelos = fact_vuelos.join(key_trafico, ["trafico"] )



key_aeropuertos.printSchema()



fact_vuelos.printSchema()



#Aeropuertos
key_aeropuertos=df_aeropuertos.alias("key_aeropuertos")


key_aeropuertos =key_aeropuertos.selectExpr("iata as origen_b","aeropuertos_key as origen_key", "ano_inicial","ano_final") 



fact_vuelos=fact_vuelos.join(key_aeropuertos, [(fact_vuelos.origen==key_aeropuertos.origen_b)&(fact_vuelos.ano >= key_aeropuertos.ano_inicial)&(fact_vuelos.ano <= key_aeropuertos.ano_final)])



fact_vuelos = fact_vuelos.drop("origen_b","ano_inicial","ano_final" )



key_aeropuertos2=df_aeropuertos.alias("key_aeropuertos2")



key_aeropuertos2 =key_aeropuertos2.selectExpr("iata as destino_b","aeropuertos_key as destino_key","ano_inicial","ano_final") 



fact_vuelos=fact_vuelos.join(key_aeropuertos2, [(fact_vuelos.destino==key_aeropuertos2.destino_b)&(fact_vuelos.ano >= key_aeropuertos2.ano_inicial)&(fact_vuelos.ano <= key_aeropuertos2.ano_final)])



fact_vuelos = fact_vuelos.drop("origen_b","ano_inicial","ano_final" )


#Transformación tabla de hechos
fact_vuelos= fact_vuelos.select("vuelos","sillas","pasajeros","carga_ofrecida","carga_bordo","fecha_key", "empresa_key", "tipo_de_vuelo_key", "trafico_key", "origen_key", "destino_key")


#Agregar columna key
fact_vuelos = fact_vuelos.withColumn(
    "vuelos_key",
    row_number().over(Window.orderBy(monotonically_increasing_id()))
)


fact_vuelos.toPandas().to_csv('fact_vuelos_v3.csv',index=False)



fact_vuelos.summary().show()

fact_vuelos.head(5)

