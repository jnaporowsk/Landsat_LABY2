@echo off
REM Krok 2 drugiej strony: kafelki + leaflet.html / openlayers.html / doc.kml przez gdal2tiles.
REM Wymaga GDAL: najlepiej uruchomic z "OSGeo4W Shell" (menu Start -> QGIS). Awaryjnie: Docker Desktop.
cd /d "%~dp0"

if not exist "wyniki\NDVI_kolor.tif" (
    echo Brak wyniki\NDVI_kolor.tif - najpierw uruchom: python ndvi_do_strony.py
    pause & exit /b 1
)
if exist strona rmdir /s /q strona

REM --- 1. GDAL juz dostepny (OSGeo4W Shell z QGIS) ---
python -c "import osgeo_utils.gdal2tiles" >nul 2>nul
if %errorlevel%==0 (
    echo Uzywam GDAL z biezacego srodowiska ^(OSGeo4W Shell^)
    python -m osgeo_utils.gdal2tiles -z 9-13 -w all -k --processes=4 wyniki\NDVI_kolor.tif strona
    goto :koniec
)

REM --- 2. QGIS w typowych lokalizacjach albo wskazany: set QGIS_DIR=C:\sciezka\do\QGIS ---
for /d %%Q in ("%QGIS_DIR%" "C:\Program Files\QGIS*" "D:\Program Files\QGIS*" "C:\OSGeo4W*" "D:\OSGeo4W*" "%LOCALAPPDATA%\Programs\QGIS*") do (
    if exist "%%~Q\bin\o4w_env.bat" (
        echo Uzywam GDAL z: %%~Q
        call "%%~Q\bin\o4w_env.bat"
        python -m osgeo_utils.gdal2tiles -z 9-13 -w all -k --processes=4 wyniki\NDVI_kolor.tif strona
        goto :koniec
    )
)

REM --- 3. Docker ---
where docker >nul 2>nul
if %errorlevel%==0 (
    echo Uzywam GDAL z obrazu Docker ghcr.io/osgeo/gdal
    docker run --rm -v "%cd%":/data ghcr.io/osgeo/gdal:ubuntu-small-latest gdal2tiles -z 9-13 -w all -k --processes=4 /data/wyniki/NDVI_kolor.tif /data/strona
    goto :koniec
)

echo Nie znaleziono GDAL. Uruchom ten plik z "OSGeo4W Shell" (menu Start -^> QGIS)
echo albo wskaz QGIS:  set QGIS_DIR=C:\sciezka\do\QGIS 3.xx
pause & exit /b 1

:koniec
if not exist "strona\leaflet.html" ( echo gdal2tiles nie utworzyl strony. & pause & exit /b 1 )
copy /y "strona\leaflet.html" "strona\index.html" >nul
echo.
echo Gotowe: folder strona\  (index.html = leaflet.html, jest tez openlayers.html i doc.kml)
echo Podglad: python -m http.server 8001 --bind 127.0.0.1 --directory strona
echo potem http://127.0.0.1:8001/
