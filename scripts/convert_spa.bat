@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
:: ... resto del codigo igual ...

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASISTENTE (ES)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [PASO 1]
set /p "INPUT_IMG=Arrastra la imagen (PNG/BMP) y pulsa Enter: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [ERROR] Archivo no encontrado.
    goto GET_IMG
)

:GET_MODE
echo.
echo [PASO 2] Selecciona el Modo GBA:
echo     1. Modo Texto (Estandar)
echo     2. Rotacion/Escalado (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Eleccion [1-2] (Defecto: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Opcion invalida. & goto GET_MODE

:GET_BPP
echo.
echo [PASO 3] Bits Por Pixel (BPP):
echo     1. 4bpp (16 colores por paleta)
echo     2. 8bpp (256 colores totales)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Eleccion [1-2] (Defecto: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Opcion invalida. & goto GET_BPP

:GET_4BPP
echo.
echo [PASO 4] Configuracion 4bpp:
echo     1. Usar Slots de Paleta personalizados
echo     2. Usar Tilemap existente (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Eleccion [1-2] (Defecto: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Arrastra el archivo .bin: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[PASO 5] Slots de paleta (ej: 0,1,2) [Defecto: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[PASO 5] Indice inicial de paleta (0-255) [Defecto: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[PASO 6] Numero de colores (1-256) [Defecto: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[PASO 7] Color Transparente (R,G,B) [Defecto: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[PASO 8] Conservar color transparente en paleta? (s/n) [n]: "
if /i "%KEEP_T%"=="s" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[PASO 9] Tiles transparentes extra al inicio [Defecto: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[PASO 10] Forzar ancho del Tileset (1-64) [Defecto: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[PASO 11] Origen del recorte (ej: 1t,1t o 8,8) [Defecto: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[PASO 12] Final del recorte (ej: 30t,18t) [Opcional]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[PASO 13] Tamano de salida (screen, bg0, 32t,20t) [Defecto: Original]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[PASO 14] Conservar archivos temporales? (s/n) [n]: "
if /i "%K_TEMP%"=="s" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[PASO 15] Guardar preview en /output? (s/n) [n]: "
if /i "%S_PREV%"=="s" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
echo Ejecutando: python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [ERROR] Fallo la conversion. ) else ( color 0A & echo [EXITO] Archivos generados. )

echo.
set /p "AGAIN=Convertir otra imagen? (s/n): "
if /i "%AGAIN%"=="s" goto START
:: Volvemos a la raiz antes de salir para que el selector funcione
cd scripts
exit /b