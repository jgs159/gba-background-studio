@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASSISTENT (DE)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [SCHRITT 1]
set /p "INPUT_IMG=Bild (PNG/BMP) hierher ziehen und Enter druecken: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [FEHLER] Datei nicht gefunden.
    goto GET_IMG
)

:GET_MODE
echo.
echo [SCHRITT 2] GBA-Modus waehlen:
echo     1. Text-Modus (Standard)
echo     2. Rotation/Skalierung (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Auswahl [1-2] (Standard: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [FEHLER] Ungueltige Auswahl. & goto GET_MODE

:GET_BPP
echo.
echo [SCHRITT 3] Bits Pro Pixel (BPP):
echo     1. 4bpp (16 Farben pro Palette)
echo     2. 8bpp (256 Farben insgesamt)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Auswahl [1-2] (Standard: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [FEHLER] Ungueltige Auswahl. & goto GET_BPP

:GET_4BPP
echo.
echo [SCHRITT 4] 4bpp Konfiguration:
echo     1. Eigene Paletten-Slots verwenden
echo     2. Vorhandene Tilemap nutzen (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Auswahl [1-2] (Standard: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Ziehen Sie die .bin-Datei hierher: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[SCHRITT 5] Paletten-Slots (z.B. 0,1,2) [Standard: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[SCHRITT 5] Startfarbindex (0-255) [Standard: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[SCHRITT 6] Anzahl der Farben (1-256) [Standard: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[SCHRITT 7] Transparente Farbe (R,G,B) [Standard: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[SCHRITT 8] Transparente Farbe in Palette behalten? (j/n) [n]: "
if /i "%KEEP_T%"=="j" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[SCHRITT 9] Extra transparente Tiles am Anfang [Standard: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[SCHRITT 10] Tileset-Breite erzwingen (1-64) [Standard: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[SCHRITT 11] Ursprung (z.B. 1t,1t oder 8,8) [Standard: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[SCHRITT 12] Ende des Zuschnitts (z.B. 30t,18t) [Optional]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[SCHRITT 13] Ausgabegroesse (screen, bg0, 32t,20t) [Standard: Original]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[SCHRITT 14] Temporaere Dateien behalten? (j/n) [n]: "
if /i "%K_TEMP%"=="j" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[SCHRITT 15] Vorschau in /output speichern? (j/n) [n]: "
if /i "%S_PREV%"=="j" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [FEHLER] Konvertierung fehlgeschlagen. ) else ( color 0A & echo [ERFOLG] Dateien erstellt. )

echo.
set /p "AGAIN=Weiteres Bild konvertieren? (j/n): "
if /i "%AGAIN%"=="j" goto START
cd scripts
exit /b