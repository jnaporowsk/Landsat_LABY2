"""Krok 1 drugiej strony: NDVI z kanałów w clipped/ -> GeoTIFF gotowy do gdal2tiles.

Zastępuje ręczny eksport z QGIS z notatnika Landsat_part2 (komórka #TODO).
Wynik (folder wyniki/):
  NDVI.tif        - NDVI jako float32, wartości od -1 do 1, poza obszarem NoData (-9999)
  NDVI8.tif       - NDVI w skali szarości 8 bit (1..255, 0 = brak danych), odpowiednik gdal_translate -ot Byte
  NDVI_kolor.tif  - NDVI pokolorowany (RGBA, przezroczysty poza obszarem) - z niego powstają kafelki

Uruchomienie z folderu Landsat8:  python ndvi_do_strony.py
"""
from pathlib import Path

import numpy as np
import rasterio
from matplotlib import colormaps

ROOT = Path(__file__).resolve().parent
CLIPPED = ROOT / 'clipped'
OUT = ROOT / 'wyniki'
NODATA = -9999


def wczytaj(numer):
    with rasterio.open(CLIPPED / f'LC_clipped_band{numer}.tif') as src:
        return src.read(1).astype('float32'), src.profile.copy()


def main():
    OUT.mkdir(exist_ok=True)
    red, profile = wczytaj(4)   # B4 - czerwony
    nir, _ = wczytaj(5)         # B5 - bliska podczerwień

    # Poza granicą obszaru piksele mają -9999; ujemne wartości to też braki/nasycenie.
    ok = (red > 0) & (nir > 0)
    # Skala 0.0001 (produkt SR C1) skraca się we wzorze, więc liczymy na DN.
    ndvi = np.full(red.shape, NODATA, dtype='float32')
    ndvi[ok] = (nir[ok] - red[ok]) / (nir[ok] + red[ok])
    ndvi[ok] = np.clip(ndvi[ok], -1, 1)

    base = profile
    base.update(driver='GTiff', compress='deflate', tiled=True, blockxsize=256, blockysize=256)

    # 1) NDVI float32
    p = base.copy(); p.update(dtype='float32', count=1, nodata=NODATA)
    with rasterio.open(OUT / 'NDVI.tif', 'w', **p) as dst:
        dst.write(ndvi, 1)

    # 2) NDVI 8 bit (szarości): -1 -> 1, +1 -> 255, brak danych -> 0
    gray = np.zeros(red.shape, dtype='uint8')
    gray[ok] = np.round((ndvi[ok] + 1) / 2 * 254 + 1).astype('uint8')
    p = base.copy(); p.update(dtype='uint8', count=1, nodata=0)
    with rasterio.open(OUT / 'NDVI8.tif', 'w', **p) as dst:
        dst.write(gray, 1)

    # 3) NDVI w kolorze (RGBA) - paleta RdYlGn: czerwony = brak roślinności, zielony = gęsta roślinność.
    #    Skala kolorów -0.2..0.9 (tam leży prawie cały NDVI obszaru); pełne -1..1 dałoby niemal jednolitą zieleń.
    rgba = (colormaps['RdYlGn'](np.clip((ndvi + 0.2) / 1.1, 0, 1)) * 255).astype('uint8')
    rgba[~ok] = 0                      # przezroczyste poza obszarem
    p = base.copy(); p.update(dtype='uint8', count=4, nodata=None, photometric='RGB', alpha='YES')  # 4. kanał = prawdziwa przezroczystość
    with rasterio.open(OUT / 'NDVI_kolor.tif', 'w', **p) as dst:
        dst.write(rgba.transpose(2, 0, 1))
        dst.colorinterp = [rasterio.enums.ColorInterp.red, rasterio.enums.ColorInterp.green,
                           rasterio.enums.ColorInterp.blue, rasterio.enums.ColorInterp.alpha]

    v = ndvi[ok]
    print(f'Ważne piksele: {ok.sum():,}  NDVI min {v.min():.3f}  średnia {v.mean():.3f}  max {v.max():.3f}')
    print(f'Zapisano: {OUT / "NDVI.tif"}, NDVI8.tif, NDVI_kolor.tif')
    print('Dalej: generuj_strone.bat')


if __name__ == '__main__':
    main()
