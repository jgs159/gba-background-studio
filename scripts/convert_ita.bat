@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASSISTENTE (IT)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [PASSO 1]
set /p "INPUT_IMG=Trascina l'immagine (PNG/BMP) e premi Invio: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [ERRORE] File non trovato.
    goto GET_IMG
)

:GET_MODE
echo.
echo [PASSO 2] Seleziona Modalita GBA:
echo     1. Modalita Testo (Standard)
echo     2. Rotazione/Scaling (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Scelta [1-2] (Default: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [ERRORE] Scelta non valida. & goto GET_MODE

:GET_BPP
echo.
echo [PASSO 3] Bits Per Pixel (BPP):
echo     1. 4bpp (16 colori per palette)
echo     2. 8bpp (256 colori totali)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Scelta [1-2] (Default: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [ERRORE] Scelta non valida. & goto GET_BPP

:GET_4BPP
echo.
echo [PASSO 4] Configurazione 4bpp:
echo     1. Usa Slot Palette personalizzati
echo     2. Usa Tilemap esistente (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Scelta [1-2] (Default: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Trascina il file .bin qui: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[PASSO 5] Slot palette (es: 0,1,2) [Default: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[PASSO 5] Indice colore iniziale (0-255) [Default: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[PASSO 6] Numero di colori (1-256) [Default: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[PASSO 7] Colore Trasparente (R,G,B) [Default: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[PASSO 8] Mantieni colore trasparente nella palette? (s/n) [n]: "
if /i "%KEEP_T%"=="s" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[PASSO 9] Tiles trasparenti extra all'inizio [Default: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[PASSO 10] Forza larghezza Tileset (1-64) [Default: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[PASSO 11] Origine ritaglio (es: 1t,1t o 8,8) [Default: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[PASSO 12] Fine ritaglio (es: 30t,18t) [Opzionale]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[PASSO 13] Dimensione output (screen, bg0, 32t,20t) [Default: Originale]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[PASSO 14] Mantieni file temporanei? (s/n) [n]: "
if /i "%K_TEMP%"=="s" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[PASSO 15] Salva anteprima in /output? (s/n) [n]: "
if /i "%S_PREV%"=="s" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [ERRORE] Conversione fallita. ) else ( color 0A & echo [SUCCESSO] File generati. )

echo.
set /p "AGAIN=Convertire un'altra immagine? (s/n): "
if /i "%AGAIN%"=="s" goto START
cd scripts
exit /b