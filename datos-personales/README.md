# Visualización de datos de sueño

Este repositorio agrupa los datasets y scripts utilizados para crear las visualizaciones expuestas en la historia 
[¿Cómo duermo?](https://app.flourish.studio/story/1044906/preview/#slide-0) 
disponible en Flourish.

Para el diseño de estas visualizaciones se partió de los datos recopilados a través del uso de un smartwatch Samsung Galaxy Watch en la app Samsung Health,
utilizando los siguientes datasets disponibles para descarga a través de la app:
- [com.samsung.health.sleep](https://developer.samsung.com/health-server/server/partner-only/api-reference/data-types/sleep.html): Contiene la información registrada sobre el inicio y fin de una noche de sueño.
- [com.samsung.health.sleep_stage](https://developer.samsung.com/health-server/server/partner-only/api-reference/data-types/sleep-stage.html): Contiene la información registrada sobre cada fase de sueño.

Estos datasets fueron procesados con un script de Python para adaptar los datos a los requerimientos de cada una de las 
visualizaciones exhibidas a lo largo de la historia:
- sueño-duracion: contiene el inicio y fin de cada noche de sueño durante el período analizado.
- sueño-fases: contiene una tabla pivot con la duración en horas de cada fase del sueño por día.
- sueño-: contiene la secuencia cíclica de fases por cada noche de sueño.
