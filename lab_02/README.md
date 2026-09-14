# Taller 2: Manipulación y creación del árbol de Merkle

**Estudiante:** Daniel Sánchez Escobar

---

## Objetivo del Taller

Implementar una solución para crear, visualizar y probar un árbol de Merkle en Python. Se busca demostrar algoritmos para resolver los problemas fundamentales de:

- **Creación del árbol dada una colección de transacciones:** Se aprovecha la naturaleza recursiva de los árboles para implementar una estrategia "Top - down", donde se "baja" recursivamente hasta las hojas y desde ahí se comienza a "subir" construyendo nuevos nodos padres, hasta llegar a la raíz.
- **El problema de la cantidad impar de transacciones:** Para este caso, se utiliza la estrategia de copiado de un nodo que se detecte impar, esto se logra al validar la longitud de la lista de transacciones que se está analizando en cada nivel y duplicando el último nodo (solo si la longitud es impar).
- **Pruebas de inclusión:** Se agregaron funciones dedicadas a la generación de la prueba, donde se busca recursivamente una transacción y se va registrando en una lista los nodos hermanos y su posición respecto al nodo de interés, desde la hoja (la transacción), pasando por cada padre en cada nivel del árbol.

---

---

## Contenido del Laboratorio

- **`taller_2.ipynb`** - Notebook Jupyter con toda la implementación, documentada con explicaciones de cada sección.
- **`README.MD`** - Este archivo con la documentación del taller.

---

## Funciones Implementadas

Redacción co-creada con Claude AI.

| Función | Descripción |
|---------|-------------|
| `Nodo.aplicar_hash()` | Método estático que calcula el hash SHA-256 de un valor dado, usado tanto para hojas como para nodos internos. |
| `Nodo.generar_copia()` | Crea una copia de un nodo existente, marcándola con `esta_copiado = True`. Se usa para duplicar el último nodo cuando la cantidad de hojas o sublistas es impar. |
| `ArbolMerkle._crear_arbol()` | Convierte la lista de transacciones en nodos hoja (aplicando SHA-256 a cada valor) y duplica la última hoja si la cantidad total es impar, antes de iniciar la construcción recursiva. |
| `ArbolMerkle._crear_arbol_recursivamente()` | Construye el árbol dividiendo la lista de nodos por la mitad de forma recursiva. Si una sublista resulta impar, duplica su último nodo. Combina pares de nodos calculando `hash(hijo_izquierdo + hijo_derecho)` hasta obtener la raíz. |
| `ArbolMerkle.get_hash_raiz()` | Retorna el valor hash almacenado en el nodo raíz del árbol, es decir, la Merkle Root. |
| `ArbolMerkle.mostrar_arbol()` | Punto de entrada para imprimir el árbol completo en pantalla, delegando en `_mostrar_arbol_recursivamente()`. |
| `ArbolMerkle._mostrar_arbol_recursivamente()` | Recorre el árbol en preorden imprimiendo el hash (truncado), el contenido, si el nodo es hoja, sus hijos y si es un nodo duplicado. |
| `ArbolMerkle.obtener_prueba_inclusion()` | Punto de entrada que genera la prueba de inclusión (Merkle proof) para un dato dado, delegando la búsqueda en `_buscar_dato_recursivamente()`. Retorna `None` si el dato no existe en el árbol. |
| `ArbolMerkle._buscar_dato_recursivamente()` | Busca recursivamente la hoja correspondiente al dato y, al encontrarla, va acumulando en la prueba el hash del nodo hermano y su posición ("izquierda"/"derecha") en cada nivel hasta la raíz. |
| `verificar_prueba_inclusion()` | Reconstruye el camino de hashes desde el dato dado hasta la raíz, combinándolo con cada hash hermano de la prueba según su posición, y compara el resultado final contra la raíz esperada. |

---

## Cómo Usar

Ejecuta las celdas del notebook en el órden de aparición.

---

*Taller del curso de Estructuras de Datos - 2026-2 - UdeA*