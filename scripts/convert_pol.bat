@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASYSTENT (PL)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [KROK 1]
set /p "INPUT_IMG=Przeciagnij obraz (PNG/BMP) i nacisnij Enter: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [BLAD] Nie znaleziono pliku.
    goto GET_IMG
)

:GET_MODE
echo.
echo [KROK 2] Wybierz tryb GBA:
echo     1. Tryb tekstowy (Standard)
echo     2. Rotacja/Skalowanie (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Wybor [1-2] (Domyslnie: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [BLAD] Nieprawidlowy wybor. & goto GET_MODE

:GET_BPP
echo.
echo [KROK 3] Gstosc bitowa (BPP):
echo     1. 4bpp (16 kolorow na palete)
echo     2. 8bpp (256 kolorow lacznie)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Wybor [1-2] (Domyslnie: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [BLAD] Nieprawidlowy wybor. & goto GET_BPP

:GET_4BPP
echo.
echo [KROK 4] Konfiguracja 4bpp:
echo     1. Uzyj wlasnych slotow palety
echo     2. Uzyj istniejacej mapy kafelkow (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Wybor [1-2] (Domyslnie: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Przeciagnij plik .bin tutaj: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[KROK 5] Sloty palety (np. 0,1,2) [Domyslnie: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[KROK 5] Poczatkowy indeks koloru (0-255) [Domyslnie: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[KROK 6] Liczba kolorow (1-256) [Domyslnie: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[KROK 7] Kolor przezroczysty (R,G,B) [Domyslnie: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[KROK 8] Zachowac przezroczysty kolor w palecie? (t/n) [n]: "
if /i "%KEEP_T%"=="t" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[KROK 9] Dodatkowe przezroczyste kafelki na poczatku [Domyslnie: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[KROK 10] Wymus szerokosc zestawu kafelkow (1-64) [Domyslnie: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[KROK 11] Punkt poczatkowy (np. 1t,1t lub 8,8) [Domyslnie: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[KROK 12] Punkt koncowy (np. 30t,18t) [Opcjonal]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[KROK 13] Rozmiar wyjsciowy (screen, bg0, 32t,20t) [Domyslnie: Oryginalny]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[KROK 14] Zachowac pliki tymczasowe? (t/n) [n]: "
if /i "%K_TEMP%"=="t" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[KROK 15] Zapisac podglad w /output? (t/n) [n]: "
if /i "%S_PREV%"=="t" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [BLAD] Konwersja nie powiodla sie. ) else ( color 0A & echo [SUKCES] Wygenerowano pliki. )

echo.
set /p "AGAIN=Konwertowac kolejny obraz? (t/n): "
if /i "%AGAIN%"=="t" goto START
cd scripts
exit /b