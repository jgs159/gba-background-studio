@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASISTEN (ID)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [LANGKAH 1]
set /p "INPUT_IMG=Seret gambar (PNG/BMP) ke sini: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [ERROR] File tidak ditemukan.
    goto GET_IMG
)

:GET_MODE
echo.
echo [LANGKAH 2] Pilih Mode GBA:
echo     1. Mode Teks (Standar)
echo     2. Mode Rotasi/Skala (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Pilihan [1-2] (Default: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Pilihan tidak valid. & goto GET_MODE

:GET_BPP
echo.
echo [LANGKAH 3] Kedalaman Bit (BPP):
echo     1. 4bpp (16 warna per palet)
echo     2. 8bpp (total 256 warna)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Pilihan [1-2] (Default: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [ERROR] Pilihan tidak valid. & goto GET_MODE

:GET_4BPP
echo.
echo [LANGKAH 4] Konfigurasi 4bpp:
echo     1. Gunakan Slot Palet Kustom
echo     2. Gunakan Tilemap yang sudah ada (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Pilihan [1-2] (Default: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Seret file .bin ke sini: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[LANGKAH 5] Slot palet (mis: 0,1,2) [Default: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[LANGKAH 5] Indeks warna awal (0-255) [Default: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[LANGKAH 6] Jumlah warna (1-256) [Default: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[LANGKAH 7] Warna Transparan (R,G,B) [Default: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=t"
set /p "KEEP_T=[LANGKAH 8] Simpan warna transparan di palet? (y/t) [t]: "
if /i "%KEEP_T%"=="y" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[LANGKAH 9] Tile transparan ekstra di awal [Default: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[LANGKAH 10] Paksa lebar Tileset (1-64) [Default: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[LANGKAH 11] Asal pemotongan (mis: 1t,1t atau 8,8) [Default: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[LANGKAH 12] Akhir pemotongan (mis: 30t,18t) [Opsional]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[LANGKAH 13] Ukuran output (screen, bg0, 32t,20t) [Default: Asli]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=t"
set /p "K_TEMP=[LANGKAH 14] Simpan file sementara? (y/t) [t]: "
if /i "%K_TEMP%"=="y" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=t"
set /p "S_PREV=[LANGKAH 15] Simpan pratinjau di /output? (y/t) [t]: "
if /i "%S_PREV%"=="y" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [ERROR] Konversi gagal. ) else ( color 0A & echo [SUKSES] File berhasil dibuat. )

echo.
set /p "AGAIN=Konversi gambar lain? (y/t): "
if /i "%AGAIN%"=="y" goto START
cd scripts
exit /b