@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - WIZARD (EN)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [STEP 1]
set /p "INPUT_IMG=Drag and drop Image (PNG/BMP) and press Enter: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [ERROR] File not found.
    goto GET_IMG
)

:GET_MODE
echo.
echo [STEP 2] Select GBA Mode:
echo     1. Text Mode (Standard)
echo     2. Rotation/Scaling (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Choice [1-2] (Default: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Invalid choice. & goto GET_MODE

:GET_BPP
echo.
echo [STEP 3] Bits Per Pixel (BPP):
echo     1. 4bpp (16 colors per palette)
echo     2. 8bpp (256 colors total)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Choice [1-2] (Default: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Invalid choice. & goto GET_BPP

:GET_4BPP
echo.
echo [STEP 4] 4bpp Configuration:
echo     1. Use Custom Palette Slots
echo     2. Use Existing Tilemap (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Choice [1-2] (Default: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Drag your .bin file here: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[STEP 5] Palette slots (e.g., 0,1,2) [Default: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[STEP 5] Starting color index (0-255) [Default: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[STEP 6] Number of colors (1-256) [Default: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[STEP 7] Transparent Color (R,G,B) [Default: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[STEP 8] Keep transparent color in palette? (y/n) [n]: "
if /i "%KEEP_T%"=="y" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[STEP 9] Extra transparent tiles at start [Default: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[STEP 10] Force Tileset width (1-64) [Default: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[STEP 11] Crop origin (e.g., 1t,1t or 8,8) [Default: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[STEP 12] Crop end (e.g., 30t,18t) [Optional]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[STEP 13] Output size (screen, bg0, 32t,20t) [Default: Original]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[STEP 14] Keep temporary files? (y/n) [n]: "
if /i "%K_TEMP%"=="y" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[STEP 15] Save preview in /output? (y/n) [n]: "
if /i "%S_PREV%"=="y" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [ERROR] Conversion failed. ) else ( color 0A & echo [SUCCESS] Assets generated. )

echo.
set /p "AGAIN=Convert another image? (y/n): "
if /i "%AGAIN%"=="y" goto START
cd scripts
exit /b