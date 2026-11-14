# Colorimetría

Prototipo digital para el análisis cuantitativo del color en imágenes, desarrollado en Python por Diego F. Peña Garnica. El repositorio reúne dos aplicaciones del mismo instrumento.

| Proyecto | Archivos |
| --- | --- |
| **Colorimetría, género y STEM.** Lienzos de un taller de co-creación con maestras en formación de Educación Infantil | `Colorimetría, género y STEM.ipynb` (cuaderno original) y la carpeta `reanalisis_2026/` (reanálisis por zonas en CIELAB) |
| **Polinizadores.** Paletas de color de plantas del agroparque | `Polinizadores.ipynb`, `DataSet.csv` (entrada), `Set_RGB.csv` (salida) y la carpeta `plantas_agroparque/` |

## Colorimetría, género y STEM

**El cuaderno original** [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/diegopenia/Colorimetria/blob/main/Colorimetr%C3%ADa%2C%20g%C3%A9nero%20y%20STEM.ipynb) es el prototipo de la primera versión del estudio:
- segmentación por bordes;
- filtro fijo de fondo (#8E7D69, umbral 45);
- K-means en RGB con K = 6 y K = 10.

**El reanálisis de noviembre de 2026** (`reanalisis_2026/`) sustituye esa configuración, porque una prueba de robustez mostró que no aislaba la figura y que los porcentajes dependían del umbral. Sus cambios son:
- parte de las fotografías originales de los lienzos;
- corrige la dominante de color con el propio papel;
- trabaja en CIELAB;
- separa cada lienzo en zonas con una máscara dibujada a mano;
- repite cada cálculo con 10 semillas, K = 4, 6 y 8 y tres umbrales de croma.

Los detalles y resultados están en [`reanalisis_2026/README.md`](reanalisis_2026/README.md).

Para reproducirlo:

```bash
pip install numpy pillow scikit-image scikit-learn matplotlib
python reanalisis_2026/reanalisis.py reanalisis_2026/lienzos salida
python reanalisis_2026/figuras.py salida
```

**Ética.** Los datos proceden de un proyecto avalado por el Comité de Ética de Investigación de la Rectoría UNIMINUTO Bogotá (Acta n.º 04 del 29 de mayo de 2023). Las fotografías de los lienzos se publican con autorización del investigador principal. Se eliminaron sus metadatos y no contienen datos que identifiquen a las participantes.

## Licencias

| Contenido | Licencia |
| --- | --- |
| Código (`.py`, `.ipynb`) | MIT (ver `LICENSE`) |
| Datos, tablas y figuras de resultados | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) |
| Fotografías de los lienzos (`reanalisis_2026/lienzos/`) | [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.es): pueden citarse y mostrarse sin fines comerciales y sin modificarlas |

## Cómo citar

Peña-Garnica, D. F. (2026). *Colorimetría: prototipo digital para el análisis cuantitativo del color* [Software]. GitHub. https://github.com/diegopenia/Colorimetria

Los metadatos de cita están en `CITATION.cff`. Cuando se archive en Zenodo, conviene citar el DOI de la versión usada.
