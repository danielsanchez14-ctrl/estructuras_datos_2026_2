# Repositorio: Laboratorios del Curso de Estructuras de Datos - 2026-2

**Autor:** Daniel Sánchez Escobar

---

## Descripción

Este repositorio contiene todos los laboratorios y talleres del curso de Estructuras de Datos correspondiente al período 2026-2.

## Estructura del Repositorio

```
estructuras_datos_2026_2/
│
├── README.md                                    # Este archivo
├── .gitignore                                   # Archivo de configuración de Git
│
├── lab_01/                                      # Laboratorio 01
│   ├── README.md                                # Documentación del laboratorio 01
│   └── taller_1.ipynb                           # Notebook de Jupyter con el taller 01
│
├── lab_02/                                      # Laboratorio 02
│   ├── README.md                                # Documentación del laboratorio 02
│   └── taller_2.ipynb                           # Notebook de Jupyter con el taller 02
│
├── lab_03/                                      # Laboratorio 03
│   ├── README.md                                # Documentación del laboratorio 03
│   ├── informe.ipynb                            # Notebook principal del laboratorio 03
│   └── ...                                      # Implementaciones y resultados del estudio
│
├── reto_1_hashing_merkle_tree/                  # Reto 1 - Hashing y Merkle Tree
│   ├── README.md                                # Documentación breve del reto 1
│   └── reto_hashing_merkle_tree.ipynb           # Notebook del reto 1
│
├── reto_2_arboles_binarios_y_b/                 # Reto 2 - Árboles binarios y B+
│   └── reto_2_arboles_binarios_y_b.ipynb       # Notebook preliminar del reto 2
│
└── ...
```

## Contenido

### Lab 01
- **Descripción:** Primer laboratorio del curso (matriz de 100.000 x 100.000 entradas).
- **Archivo Principal:** `taller_1.ipynb` (Notebook Jupyter).
- **Datos:** `matriz.txt` (Debe generarse cada vez que se clone el repositorio).
- **Documentación:** [Laboratorio 1](lab_01/README.md).

### Lab 02
- **Descripción:** Segundo laboratorio del curso (Merkle Tree).
- **Archivo Principal:** `taller_2.ipynb` (Notebook Jupyter).
- **Documentación:** [Laboratorio 2](lab_02/README.md).

### Lab 03
- **Descripción:** Tercera entrega del curso, centrada en la comparación experimental de una lista, un ABB y un árbol B+ para manejar estudiantes por ID.
- **Archivo Principal:** `informe.ipynb` (Notebook Jupyter).
- **Temas principales:** búsquedas, inserciones, listados ordenados y consultas por rango; análisis de rendimiento frente a distintos tamaños de entrada y orden de datos.
- **Documentación:** [Laboratorio 3](lab_03/README.md).

### Reto 1 - Hashing y Merkle Tree
- **Descripción:** Reto centrado en funciones hash y la construcción de un árbol Merkle para validar integridad y estructura de datos.
- **Archivo Principal:** `reto_hashing_merkle_tree.ipynb` (Notebook Jupyter).
- **Documentación:** [README del reto 1](reto_1_hashing_merkle_tree/README.md).

### Reto 2 - Árboles binarios y B+
- **Descripción:** Preludio del laboratorio 3. En este reto se explora el comportamiento de estructuras basadas en árboles, con énfasis en la comparación entre ABB y árboles B+ para búsquedas y recorridos.
- **Archivo Principal:** `reto_2_arboles_binarios_y_b.ipynb` (Notebook Jupyter).
- **Relación con el laboratorio 3:** sirve como base conceptual y experimental para el análisis más completo desarrollado en [Laboratorio 3](lab_03/README.md).

---

*Última actualización: 2026-10-07*