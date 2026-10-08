# Laboratorio 3: Sistema de Búsqueda

La redacción de este documento fue realizada con la asistencia de una IA generativa (GitHub Copilot, asistente de codificación de Visual Studio Code) y revisada por Daniel Sánchez Escobar.

**Estudiante:** Daniel Sánchez Escobar

---

## Objetivo del Laboratorio

Implementar y comparar experimentalmente tres estrategias para administrar estudiantes por ID en Python:

- **Lista** nativa de Python.
- **Árbol binario de búsqueda (ABB)**.
- **Árbol B+**.

El laboratorio busca responder cómo cambia el tiempo de ejecución de las operaciones principales cuando se incrementa la cantidad de datos (`N`), y cómo afecta el orden de inserción de los IDs (aleatorio u ordenado). Las operaciones evaluadas son:

- Búsqueda por ID.
- Inserción.
- Listado ordenado.
- Búsqueda por rango de IDs.

---

## Contenido del Laboratorio

- **`informe.ipynb`**: notebook principal con la implementación, la metodología experimental y la interpretación de resultados.
- **`graficas/`**: imágenes generadas por los experimentos del estudio.
- **`resultados/`**: archivos CSV con los tiempos medidos por prueba.
- **`ABB.py`**: implementación del árbol binario de búsqueda.
- **`ArbolBPlus.py`**: implementación del árbol B+.
- **`GestorListaEstudiantes.py`**: implementación de la estructura basada en lista.
- **`Estructura.py`**: interfaz base común para todas las estructuras.
- **`funciones_auxiliares.py`**: funciones para generar estudiantes, búsquedas y mediciones de tiempo.
- **`README.md`**: documentación del laboratorio.

---

## Estructuras Evaluadas

### 1. Lista
La lista guarda los estudiantes en el orden en que se insertan. Las operaciones se vuelven costosas cuando se requiere consultar, ordenar o filtrar muchos registros.

- **Búsqueda por ID**: lineal, O(N).
- **Listado**: requiere ordenar la copia con `sorted` antes de devolver los resultados.
- **Búsqueda por rango**: recorre todos los elementos para filtrar una subsección.

### 2. ABB
El árbol binario de búsqueda organiza los IDs por orden, permitiendo búsquedas más rápidas cuando el árbol está balanceado.

- **Búsqueda por ID**: O(log N) esperado en datos aleatorios.
- **Inserción**: O(log N) esperado en árboles balanceados.
- **Listar en orden**: recorrido inorden.
- **Punto crítico**: si los IDs llegan ordenados, el ABB se degenera y se vuelve casi lineal.

### 3. Árbol B+
El árbol B+ mantiene balanceo estructural y almacena los datos en hojas enlazadas, lo cual favorece búsquedas por rango y listado ordenado.

- **Búsqueda por ID**: se desciende por niveles; crecimiento logarítmico.
- **Listado**: recorre las hojas enlazadas, muy eficiente.
- **Rango de IDs**: se mueve entre hojas contiguas y devuelve los registros en orden.
- **Ventaja clave**: mantiene buen comportamiento tanto en búsquedas puntuales como en recorridos secuenciales.

---

## Metodología Experimental

La comparación se realizó con varias configuraciones:

- Tamaños de entrada: `N = 100`, `1000`, `10000`, `100000`.
- Orden de inserción: IDs aleatorios y IDs ordenados.
- Búsquedas puntuales por lote: `M = 1000`.
- Búsquedas por rango: `M = 100`, con rango fijo de `k = 50` estudiantes.
- Repeticiones: 30 por configuración.
- Mediciones con reloj de alta precisión (`time.perf_counter_ns()`).
- Se descartaron 3 ejecuciones de calentamiento para reducir ruido del sistema.

La idea central fue comparar el crecimiento del tiempo frente a `N` y verificar si el comportamiento observado se ajusta a la complejidad teórica de cada estructura.

Sobre los tiempos medidos, es importante recalcar que el objetivo del laboratorio es evaluar cómo escala el costo temporal de cada operación (búsqueda, inserción, listado y rangos) al aumentar el tamaño de los datos ($N$), validando así las complejidades teóricas ($O(N)$, $O(\log N)$, $O(N \log N)$). Dado que una operación individual en estructuras jerárquicas como el ABB o el Árbol B+ se ejecuta en pocos microsegundos, las mediciones crudas del sistema se capturan en nanosegundos ($ns$).

Para facilitar la lectura en las tablas de resumen, los tiempos se convierten a microsegundos ($\mu s$) o milisegundos ($ms$) según el experimento para evitar notaciones recargadas de ceros. En las gráficas logarítmicas, el eje vertical se estandariza en segundos ($s$), permitiendo comparar de forma uniforme y sin distorsiones tanto las ejecuciones unitarias como los lotes acumulados ($M$ consultas). 
---

## Experimentos Realizados

### Experimento 0: Pruebas de correctitud
Se validó que las tres estructuras entregaran los mismos resultados para las operaciones básicas:

- `insertar`
- `buscar`
- `listar`
- `buscar_rango_id`

Se probaron casos con datos aleatorios, ordenados y descendentes, además de valores vacíos y rangos límite. El resultado fue exitoso: no hubo fallos de correctitud.

### Experimento 1: Tiempo acumulado de búsquedas aleatorias vs N
Se midió el tiempo total de ejecutar `M = 1000` búsquedas con IDs aleatorios. La tendencia esperada fue:

- Lista: crecimiento claramente lineal y más alto al aumentar `N`.
- ABB: crecimiento casi logarítmico en datos aleatorios.
- Árbol B+: mejor desempeño estable en este escenario.

### Experimento 2: Tiempo de construcción vs N (IDs aleatorios)
Se comparó el costo de insertar `N` estudiantes con IDs aleatorios. En esta configuración, el ABB y el Árbol B+ muestran un crecimiento mucho más suave que la lista.

### Experimento 3: Tiempo de construcción vs N (IDs ordenados)
Este experimento fue importante para mostrar el caso degenerado del ABB. Al insertar IDs ya ordenados, el árbol pierde balance y su altura crece casi linealmente con `N`.

- **ABB**: mucho peor que en el caso aleatorio.
- **Lista**: el crecimiento es predecible, pero sigue siendo peor que un árbol balanceado para búsquedas repetidas.
- **Árbol B+**: conserva un comportamiento mucho más estable y ordenado.

### Experimento 4: Relación entre altura y tiempo de búsqueda
Se relacionó la altura del ABB con el tiempo de búsqueda. El estudio confirma que, cuando la estructura se degenera, el costo de búsqueda se parece más a un recorrido secuencial que a una búsqueda logarítmica.

### Experimento 5: Búsqueda contra M, con N fijo
Se mantuvo `N` constante y se aumentó el número de búsquedas por lote (`M`). El comportamiento muestra que el costo total crece casi linealmente con `M`, pero con distintas pendientes según la estructura. El Árbol B+ y el ABB balanceado escalan mejor que la lista.

### Experimento 6: Tiempo de listado ordenado vs N
Se evaluó el costo de obtener todos los estudiantes ordenados por ID. En este caso, el Árbol B+ tuvo un desempeño especialmente bueno debido a su organización por hojas enlazadas. El ABB también se comporta bien, pero su ventaja depende del balance del árbol.

### Experimento 7: Búsqueda por rango vs N (K = 50 fijo)
Se evaluaron rangos fijos con exactamente 50 estudiantes. La búsqueda por rango es una operación donde el Árbol B+ suele destacar porque puede recorrer hojas contiguas de forma muy eficiente. La lista, aunque simple, requiere recorrer más datos para responder la consulta.

---

## Hallazgos Principales

- La estructura más simple, la **lista**, ofrece un costo muy bajo para pocas entradas, pero se vuelve claramente más lenta a medida que crece `N`.
- El **ABB** presenta muy buen comportamiento cuando los IDs están distribuidos de manera aleatoria, pero se degrada cuando los datos se insertan ya ordenados.
- El **árbol B+** fue la estructura más consistente en casi todos los experimentos, especialmente en listado y consultas por rango.
- Las diferencias entre estructuras se vuelven más evidentes a partir de tamaños de entrada moderados y grandes (mil, diez mil o más registros).
- La complejidad teórica se refleja claramente en los resultados experimentales: crecimiento lineal para la lista y crecimiento logarítmico para estructuras indexadas bajo condiciones normales.

---

## Conclusión

El laboratorio confirma que la elección de la estructura de datos tiene un impacto directo sobre el tiempo de ejecución y la escalabilidad del sistema. Para búsquedas puntuales y consultas frecuentes por ID, una estructura indexada como el ABB o el árbol B+ resulta mucho más eficiente que una lista lineal. Sin embargo, el ABB requiere atención especial: en escenarios con inserción ordenada, su altura puede crecer y perder la ventaja esperada.

En cambio, el árbol B+ ofrece una solución más robusta y estable para operaciones de listado y intervalo, y por ello resulta particularmente apropiado para sistemas donde se manejan datos grandes y se necesitan consultas frecuentes por rango.

---

## Requisitos y Ejecución

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Los resultados y análisis se encuentran en el notebook `informe.ipynb`.

3. Revisar los resultados en la carpeta `resultados/` y las gráficas generadas en `graficas/`.

4. Si deseas reproducir la validación de correctitud, vuelve a ejecutar las celdas correspondientes del notebook.

---

## Nota Final

Este laboratorio se desarrolló con enfoque experimental y comparativo, buscando conectar la teoría de estructuras de datos con métricas reales de rendimiento. Los resultados muestran cómo la misma operación puede variar drásticamente según la estructura elegida, y por qué el diseño de la base de datos o del sistema de almacenamiento debe responder a las necesidades concretas de acceso a la información.

*Laboratorio del curso de Estructuras de Datos - 2026-2 - UdeA*
