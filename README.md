# Landsat 8: NDVI dla Krakowa i strona z kafelkami (gdal2tiles)

Druga strona projektu NASA/Landsat. Liczymy NDVI ze sceny Landsat 8 z 7 sierpnia 2013
(`LC08_L1TP_188025_20130807_20170503_01_T1`, Collection 1 Surface Reflectance), przyciętej do granicy
z `vector/krakow_krakowskie.shp`, i publikujemy wynik jako mapę wygenerowaną przez **gdal2tiles**
(`leaflet.html`, `openlayers.html`, `doc.kml` dla Google Earth).

Pierwsza strona (NDVI/NDBI/MNDWI/RGB w Pythonie) jest w repozytorium `Landsat_LABY`.

## Zawartość

| Plik / folder | Opis |
|---|---|
| `Landsat_part1.ipynb` | wczytanie kanałów, podgląd |
| `Landsat_part2.ipynb` | przycięcie do granicy, NDVI / NDBI / NDWI |
| `Landsat.py` | ten sam kod co w notatnikach, jako skrypt |
| `clipped/` | kanały 1–7 przycięte do granicy Krakowa (wejście dla dalszych kroków) |
| `vector/` | granica obszaru (SHP, EPSG:32634 – brak pliku .prj) |
| `ndvi_do_strony.py` | NDVI z `clipped/` → `wyniki/NDVI.tif`, `NDVI8.tif`, `NDVI_kolor.tif` |
| `generuj_strone.bat` | gdal2tiles → folder `strona/` z kafelkami i stronami HTML |

`LC08/` (pełna scena, ~1,2 GB) nie jest w repozytorium – pliki przekraczają limit GitHuba.
Dostępna u prowadzącego. Do wygenerowania strony wystarczy `clipped/`.

## Uruchomienie (Windows)

Wymagane: Python z bibliotekami z `requirements.txt` oraz GDAL – z **QGIS** (qgis.org)
albo z **Docker Desktop**.

```bat
pip install -r requirements.txt
python ndvi_do_strony.py
generuj_strone.bat
python -m http.server 8001 --bind 127.0.0.1 --directory strona
```

Otwórz http://127.0.0.1:8001/ (to samo co `leaflet.html`; jest też `openlayers.html`).

Odpowiednik poleceń z notatnika (OSGeo4W Shell z QGIS):

```bat
gdal_translate -of GTiff -ot Byte -scale -1 1 1 255 -a_nodata 0 wyniki\NDVI.tif wyniki\NDVI8.tif
gdal2tiles -s EPSG:32634 -k -z 9-13 wyniki\NDVI8.tif strona
```

## Publikacja na koncie AGH (VPN AGH włączony)

```bat
ssh LOGIN@student.agh.edu.pl "mkdir -p public_html/landsat_ndvi"
scp -r strona\* LOGIN@student.agh.edu.pl:public_html/landsat_ndvi/
ssh LOGIN@student.agh.edu.pl "find public_html/landsat_ndvi -type d -exec chmod 755 {} + ; find public_html/landsat_ndvi -type f -exec chmod 644 {} + ; chmod o+x ~"
```

Adres: `https://student.agh.edu.pl/~LOGIN/landsat_ndvi/`

## Uwagi

- NDVI = (B5 − B4) / (B5 + B4). Skala 0,0001 produktu SR skraca się we wzorze.
- Piksele poza granicą (-9999) i z wartościami ≤ 0 są pomijane.
- Kafelki dla zoomów 9–13; większe powiększenie nie doda szczegółów (rozdzielczość 30 m).

Kod bazowy: S. Moliński.
