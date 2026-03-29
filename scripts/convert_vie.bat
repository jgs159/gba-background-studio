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
echo       GBA BACKGROUND STUDIO - TRO LY (VI)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [BUOC 1]
set /p "INPUT_IMG=Keo va tha hinh anh (PNG/BMP) vao day: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [LOI] Khong tim thay tep.
    goto GET_IMG
)

:GET_MODE
echo.
echo [BUOC 2] Chon che do GBA:
echo     1. Che do van ban (Text Mode)
echo     2. Che do xoay/thu phong (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Lua chon [1-2] (Mac dinh: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [LOI] Lua chon khong hop le. & goto GET_MODE

:GET_BPP
echo.
echo [BUOC 3] Do sau bit (BPP):
echo     1. 4bpp (16 mau moi bang mau)
echo     2. 8bpp (tong cong 256 mau)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Lua chon [1-2] (Mac dinh: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [LOI] Lua chon khong hop le. & goto GET_MODE

:GET_4BPP
echo.
echo [BUOC 4] Cau hinh 4bpp:
echo     1. Su dung cac o bang mau tuy chinh
echo     2. Su dung Tilemap da co (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Lua chon [1-2] (Mac dinh: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Keo tep .bin vao day: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[BUOC 5] Cac o bang mau (vd: 0,1,2) [Mac dinh: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[BUOC 5] Chi so mau bat dau (0-255) [Mac dinh: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[BUOC 6] So luong mau (1-256) [Mac dinh: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[BUOC 7] Mau trong suot (R,G,B) [Mac dinh: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=k"
set /p "KEEP_T=[BUOC 8] Giu mau trong suot trong bang mau? (c/k) [k]: "
if /i "%KEEP_T%"=="c" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[BUOC 9] Cac o tile trong suot bo sung o dau [Mac dinh: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[BUOC 10] Bat buoc chieu rong Tileset (1-64) [Mac dinh: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[BUOC 11] Diem bat dau cat (vd: 1t,1t hoac 8,8) [Mac dinh: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[BUOC 12] Diem ket thuc cat (vd: 30t,18t) [Tuy chon]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[BUOC 13] Kich thuoc dau ra (screen, bg0, 32t,20t) [Mac dinh: Goc]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=k"
set /p "K_TEMP=[BUOC 14] Giu lai cac tep tam thoi? (c/k) [k]: "
if /i "%K_TEMP%"=="c" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=k"
set /p "S_PREV=[BUOC 15] Luu anh xem truoc trong /output? (c/k) [k]: "
if /i "%S_PREV%"=="c" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [LOI] Chuyen doi that bai. ) else ( color 0A & echo [THANH CONG] Da tao cac tep. )

echo.
set /p "AGAIN=Chuyen doi hinh anh khac? (c/k): "
if /i "%AGAIN%"=="c" goto START
cd scripts
exit /b