import numpy as np
import pandas as pd

# import data
df = pd.read_csv('datos-personales-fases.csv')
sleep_eff = pd.read_csv('datos-personales-eficiencia.csv')

# Corrección de fecha por zona horaria
df.start_time = pd.to_datetime(
    df.start_time,
    format='%Y-%m-%d %H:%M:%S.%f').dt.tz_localize('UTC').dt.tz_convert(
        'America/Argentina/Catamarca').dt.tz_localize(None)

df.end_time = pd.to_datetime(
    df.end_time,
    format='%Y-%m-%d %H:%M:%S.%f').dt.tz_localize('UTC').dt.tz_convert(
        'America/Argentina/Catamarca').dt.tz_localize(None)

df.drop(labels='time_offset', axis=1, inplace=True)

# Equivalencias de códigos de fases
df.stage = df.stage.map({
    40001: 'Despierto',
    40002: 'Ligero',
    40003: 'Profundo',
    40004: 'REM'
})

# Cálculo de duración total en segundos
df['duration_secs'] = (df.end_time -
                       df.start_time).dt.total_seconds().astype('int64')

# Generar DataFrame con tiempo total de sueño
df_total = pd.merge(left=df.groupby('sleep_id')['start_time'].agg(
    'min').to_frame().reset_index(),
                    right=df.groupby('sleep_id')['end_time'].agg(
                        'max').to_frame().reset_index(),
                    how='inner',
                    on='sleep_id')
df_total = pd.merge(left=df_total, right=sleep_eff, how='left', on='sleep_id')

df_total['duration_secs'] = (
    df_total.end_time - df_total.start_time).dt.total_seconds().astype('int64')

# DataFrame para Visualización "Tiempo de Sueño" en Flourish
df_melted = pd.DataFrame(
    {
        'fecha': df_total.start_time.dt.strftime('%Y-%m-%d'),
        'inicio': df_total.start_time.dt.strftime('%H%M%S'),
        'fin': df_total.end_time.dt.strftime('%H%M%S')
    },
    dtype='object')

df_melted = pd.melt(
    df_melted,
    id_vars='fecha',  #['fecha', 'hora_inicio', 'hora_fin'],
    value_vars=['inicio', 'fin'],
    var_name='momento',
    value_name='valor').set_index('fecha')
df_melted.valor = df_melted.valor.astype('int64') / 10000
df_melted['entero'] = df_melted.valor.apply(np.floor)
df_melted['decimal'] = (df_melted.valor - df_melted.entero) / 60 * 100
df_melted.valor = df_melted.entero + df_melted.decimal
df_melted.drop(labels=['entero', 'decimal'], axis=1, inplace=True)
df_melted = pd.merge(left=df_melted,
                     right=pd.DataFrame({
                         'fecha':
                         df_total.start_time.dt.strftime('%Y-%m-%d'),
                         'eficiencia':
                         df_total.efficiency,
                         'duracion':
                         df_total.duration_secs
                     }).set_index('fecha'),
                     how='left',
                     left_index=True,
                     right_index=True)
df_melted['duracion_hhmm'] = df_melted.duracion.apply(
    lambda x: pd.Timedelta(seconds=x)).astype('str').map(lambda x: x[7:12])
dias_semana = {
    '2021-11-03': 'Miércoles 3 de noviembre',
    '2021-11-04': 'Jueves 4 de noviembre',
    '2021-11-05': 'Viernes 5 de noviembre',
    '2021-11-06': 'Sábado 6 de noviembre',
    '2021-11-07': 'Domingo 7 de noviembre',
    '2021-11-08': 'Lunes 8 de noviembre',
    '2021-11-09': 'Martes 9 de noviembre',
    '2021-11-10': 'Miércoles 10 de noviembre',
    '2021-11-11': 'Jueves 11 de noviembre',
    '2021-11-12': 'Viernes 12 de noviembre',
    '2021-11-13': 'Sábado 13 de noviembre',
    '2021-11-14': 'Domingo 14 de noviembre',
    '2021-11-15': 'Lunes 15 de noviembre',
    '2021-11-16': 'Martes 16 de noviembre',
    '2021-11-17': 'Miércoles 17 de noviembre',
    '2021-11-18': 'Jueves 18 de noviembre'
}
df_melted['día'] = df_melted.index.map(dias_semana)

fin_de_semana = {
    '2021-11-03': 'Día de Semana',
    '2021-11-04': 'Día de Semana',
    '2021-11-05': 'Día de Semana',
    '2021-11-06': 'Fin de Semana',
    '2021-11-07': 'Fin de Semana',
    '2021-11-08': 'Día de Semana',
    '2021-11-09': 'Día de Semana',
    '2021-11-10': 'Día de Semana',
    '2021-11-11': 'Día de Semana',
    '2021-11-12': 'Día de Semana',
    '2021-11-13': 'Fin de Semana',
    '2021-11-14': 'Fin de Semana',
    '2021-11-15': 'Día de Semana',
    '2021-11-16': 'Día de Semana',
    '2021-11-17': 'Día de Semana',
    '2021-11-18': 'Día de Semana'
}
df_melted['grupo'] = df_melted.index.map(fin_de_semana)

# DataFrame para Visualización "(%) Distribución del Sueño por Fases" en Flourish
df['fecha'] = df.start_time.dt.strftime('%Y-%m-%d')
df_pivot = df[['fecha', 'stage', 'duration_secs'
               ]].pivot_table(index='fecha',
                              columns='stage',
                              values='duration_secs',
                              aggfunc=lambda x: sum(x / 3600)).fillna(0)
df_pivot = df_pivot[['Despierto', 'REM', 'Ligero', 'Profundo']]

# DataFrame para Visualización "Fases del Sueño" en Flourish
df_hypno = pd.DataFrame({
    'fecha':
    df.start_time.dt.strftime('%Y-%m-%d'),
    'hora_inicio':
    df.start_time.dt.strftime('%H:%M:%S'),
    'hora_fin':
    df.end_time.dt.strftime('%H:%M:%S'),
    'inicio':
    df.start_time.dt.strftime('%H%M%S').astype('int64') / 10000,
    'fin':
    df.end_time.dt.strftime('%H%M%S').astype('int64') / 10000,
    'fase':
    df.stage,
    'codigo_fase':
    df.stage.map({
        'Despierto': 4,
        'REM': 3,
        'Ligero': 2,
        'Profundo': 1
    }),
    'orden':
    np.arange(1,
              len(df) + 1)
})
hypno_inicio = df_hypno[[
    'fecha', 'hora_inicio', 'inicio', 'codigo_fase', 'fase', 'orden'
]]
hypno_fin = df_hypno[[
    'fecha', 'hora_fin', 'fin', 'codigo_fase', 'fase', 'orden'
]]
hypno_inicio.columns = [
    'fecha', 'hora', 'valor', 'codigo_fase', 'fase', 'orden'
]
hypno_fin.columns = ['fecha', 'hora', 'valor', 'codigo_fase', 'fase', 'orden']
df_hypno = pd.concat([hypno_inicio, hypno_fin])
df_hypno['entero'] = df_hypno.valor.apply(np.floor)
df_hypno['decimal'] = (df_hypno.valor - df_hypno.entero) / 60 * 100
df_hypno.valor = df_hypno.entero + df_hypno.decimal
df_hypno.drop(labels=['entero', 'decimal'], axis=1, inplace=True)
df_hypno['día'] = df_hypno.fecha.map(dias_semana)

# Exportación de Datasets
df.sort_values(by='start_time').to_csv('sueño-base.csv', index=False)
df_total.sort_values(by='start_time').to_csv('sueño-total.csv', index=False)
df_melted.sort_values(by='fecha').to_csv('sueño-duracion.csv')
df_pivot.to_csv('sueño-fases.csv')
df_hypno.sort_values(by=['orden', 'fecha', 'valor']).to_csv('sueño-ciclos.csv',
                                                            index=False)
