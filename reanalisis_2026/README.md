# Reanálisis colorimétrico por zonas (noviembre de 2026)

Análisis de los dos lienzos colectivos del taller de co-creación, para el artículo *Representaciones de la ciencia y de las científicas en futuras maestras de Educación Infantil*.

## Procedimiento
- **Entrada.** `lienzos/A.jpg` y `lienzos/B.jpg`, fotografías originales sin metadatos. El script las reduce a 1/4 de su tamaño.
- **Balance de blancos.** Se toma como referencia el papel, con los píxeles claros y poco saturados que están fuera de la figura.
- **Espacio de color.** CIELAB (D65).
- **Zonas.** Cada lienzo se divide con una máscara dibujada a mano (diccionario `MASK` de `reanalisis.py`, ver `resultados/F1_mascaras_propuestas.png`):
  - **Figura.**
  - **Elementos asociados.** En el Lienzo A, la planta, las guirnaldas y los charcos; en el Lienzo B, la bombilla, los engranajes y el robot.
  - **Texto.** Solo en el Lienzo B.
  - **Resto del lienzo.**
- **Píxeles sin color.** Los que tienen croma C*ab < 15. También se prueban los umbrales 10 y 20.
- **Métricas por zona:**
  - proporción sin color;
  - croma media (de toda la zona y de los píxeles con color);
  - familias de tono;
  - paleta K-means en CIELAB y diferencia de color media ΔE2000 entre sus tonos.
- **Robustez.** 10 semillas × K = 4, 6 y 8 × tres umbrales de croma: 540 corridas en `resultados/robustez_paletas.csv`.

## Resultados de la figura (umbral 15; rango con umbrales de 10 a 20)

| Métrica | Lienzo A | Lienzo B |
| --- | --- | --- |
| Píxeles sin color | 16 % (11–41 %) | 57 % (36–62 %) |
| Croma media de toda la figura | 23,1 | 25,4 |
| Croma media de los píxeles con color | 26,0 (25,3–29,4) | 48,7 (36,9–53,4) |
| Familias de tono | marrón 58 %, rojo 22 %, rosa/magenta 16 % | azul 36 %, naranja 27 %, amarillo 23 % |
| ΔE2000 medio de la paleta K = 6 | 21,8 (19,2–23,4) | 39,2 (33,9–41,1) |

Los valores son descriptores exploratorios de dos casos y no permiten inferencias estadísticas.

## Archivos
- **`reanalisis.py`.** Uso: `python reanalisis.py <carpeta con A.jpg y B.jpg> <salida>`.
- **`figuras.py`.** Uso: `python figuras.py <salida>`. Se ejecuta después de `reanalisis.py`.
- **`resultados/`.** Métricas por zona (CSV y JSON), paletas, corridas de robustez y figuras.
