# Taller 1: Manipulación Eficiente de Matrices Grandes en Disco

**Estudiante:** Daniel Sánchez Escobar

---

## Objetivo del Taller

Implementar una solución para crear, almacenar y manipular una matriz de 100,000 × 100,000 elementos directamente en disco, demostrando cómo resolver los problemas fundamentales de:

- **Consumo excesivo de RAM:** Cargar una matriz de ese tamaño en memoria es inviable (~10 GB). La solución utiliza acceso directo a disco mediante `seek()` y aritmética de offsets.
- **Escritura lenta a disco:** Se implementa un generador lazy que produce filas bajo demanda, permitiendo que `writelines()` escriba eficientemente sin cargar toda la matriz en memoria.
- **Optimización en manipulación, almacenamiento y lectura:** Acceso O(1) a cualquier elemento o fila sin necesidad de leer el archivo desde el inicio.

---

## Contenido del Laboratorio

- **`taller_1.ipynb`** - Notebook Jupyter con toda la implementación, bien documentada con explicaciones de cada sección.
- **`README.MD`** - Este archivo con la documentación del taller.

---

## Funciones Implementadas

| Función | Descripción |
|---------|-------------|
| `crear_matriz()` | Genera la matriz de 100,000 × 100,000 en disco con filas alternadas de 0s y 1s usando un generador lazy. Metadatos en la primera línea. |
| `verificar_matriz()` | Valida que las dimensiones declaradas en metadatos coincidan con el tamaño real del archivo en bytes. |
| `leer_metadata()` | Extrae y muestra los metadatos de la matriz (número de filas y columnas). |
| `_info_archivo()` | Función auxiliar que calcula offsets necesarios para acceso directo: header_len, filas, columnas, row_len. |
| `mostrar_fila()` | Lee una fila completa especificada por número (iniciando en 1), mostrando una cantidad personalizable de entradas. |
| `mostrar_bloque()` | Muestra una porción rectangular de la matriz definida por rangos de filas y columnas. |
| `mostrar_entrada()` | Obtiene y muestra un elemento individual dados los índices de fila y columna. |
| `modificar_elemento()` | Modifica un elemento específico de la matriz escribiendo directamente en el archivo. |

---

## Cómo Usar

1. Ejecutar la celda de **creación** para generar la matriz en disco.
2. Ejecutar la celda de **validación** para verificar que los datos se guardaron correctamente.
3. Utilizar las funciones de lectura para acceder a datos específicos sin cargar todo a memoria:
   - `leer_metadata()` - Para ver dimensiones
   - `mostrar_entrada(fila, columna)` - Para un elemento específico
   - `mostrar_fila(numero_fila)` - Para una fila completa
   - `mostrar_bloque(fi, ff, ci, cf)` - Para un bloque de datos
4. Utilizar `modificar_elemento(fila, columna, valor)` para actualizar elementos individuales.



*Taller del curso de Estructuras de Datos - 2026-2 - UdeA*