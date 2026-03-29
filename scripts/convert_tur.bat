@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASISTAN (TR)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [ADIM 1]
set /p "INPUT_IMG=Resmi (PNG/BMP) buraya surukleyin ve Enter'a basin: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [HATA] Dosya bulunamadi.
    goto GET_IMG
)

:GET_MODE
echo.
echo [ADIM 2] GBA Modunu Secin:
echo     1. Metin Modu (Standart)
echo     2. Dondurme/Olcekleme (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Secim [1-2] (Varsayilan: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [HATA] Gecersiz secim. & goto GET_MODE

:GET_BPP
echo.
echo [ADIM 3] Piksel Basina Bit (BPP):
echo     1. 4bpp (Palet basina 16 renk)
echo     2. 8bpp (Toplam 256 renk)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Secim [1-2] (Varsayilan: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [HATA] Gecersiz secim. & goto GET_MODE

:GET_4BPP
echo.
echo [ADIM 4] 4bpp Yapilandirmasi:
echo     1. Ozel Palet Yuvalarini Kullan
echo     2. Mevcut Tilemap Kullan (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Secim [1-2] (Varsayilan: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   .bin dosyasini buraya surukleyin: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[ADIM 5] Palet yuvalari (orn: 0,1,2) [Varsayilan: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[ADIM 5] Baslangic renk indeksi (0-255) [Varsayilan: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[ADIM 6] Renk sayisi (1-256) [Varsayilan: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[ADIM 7] Seffaf Renk (R,G,B) [Varsayilan: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[ADIM 8] Seffaf renk palette korunsun mu? (e/h) [h]: "
if /i "%KEEP_T%"=="e" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[ADIM 9] Baslangicta ekstra seffaf tilelar [Varsayilan: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[ADIM 10] Tileset genisligini zorla (1-64) [Varsayilan: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[ADIM 11] Kirpma baslangici (orn: 1t,1t veya 8,8) [Varsayilan: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[ADIM 12] Kirpma sonu (orn: 30t,18t) [Opsiyonel]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[ADIM 13] Cikis boyutu (screen, bg0, 32t,20t) [Varsayilan: Orijinal]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[ADIM 14] Gecici dosyalar korunsun mu? (e/h) [h]: "
if /i "%K_TEMP%"=="e" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[ADIM 15] Onizleme /output klasorune kaydedilsin mi? (e/h) [h]: "
if /i "%S_PREV%"=="e" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [HATA] Donusturme basarisiz oldu. ) else ( color 0A & echo [BASARILI] Dosyalar olusturuldu. )

echo.
set /p "AGAIN=Baska bir resim donusturulsun mu? (e/h): "
if /i "%AGAIN%"=="e" goto START
cd scripts
exit /b