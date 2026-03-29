@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASSISTENT (NL)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [STAP 1]
set /p "INPUT_IMG=Sleep afbeelding (PNG/BMP) hier en druk op Enter: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [FOUT] Bestand niet gevonden.
    goto GET_IMG
)

:GET_MODE
echo.
echo [STAP 2] Selecteer GBA-modus:
echo     1. Tekstmodus (Standaard)
echo     2. Rotatie/Schalen (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Keuze [1-2] (Standaard: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [FOUT] Ongeldige keuze. & goto GET_MODE

:GET_BPP
echo.
echo [STAP 3] Bits per pixel (BPP):
echo     1. 4bpp (16 kleuren per palet)
echo     2. 8bpp (256 kleuren totaal)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Keuze [1-2] (Standaard: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [FOUT] Ongeldige keuze. & goto GET_BPP

:GET_4BPP
echo.
echo [STAP 4] 4bpp configuratie:
echo     1. Gebruik aangepaste paletslots
echo     2. Gebruik bestaande Tilemap (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Keuze [1-2] (Standaard: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Sleep het .bin-bestand hierheen: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[STAP 5] Paletslots (bijv. 0,1,2) [Standaard: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[STAP 5] Startkleurindex (0-255) [Standaard: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[STAP 6] Aantal kleuren (1-256) [Standaard: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[STAP 7] Transparante kleur (R,G,B) [Standaard: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[STAP 8] Transparante kleur in palet behouden? (j/n) [n]: "
if /i "%KEEP_T%"=="j" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[STAP 9] Extra transparante tegels aan begin [Standaard: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[STAP 10] Forceer Tileset breedte (1-64) [Standaard: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[STAP 11] Oorsprong bijsnijden (bijv. 1t,1t of 8,8) [Standaard: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[STAP 12] Einde bijsnijden (bijv. 30t,18t) [Optioneel]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[STAP 13] Uitvoerformaat (screen, bg0, 32t,20t) [Standaard: Origineel]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[STAP 14] Tijdelijke bestanden bewaren? (j/n) [n]: "
if /i "%K_TEMP%"=="j" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[STAP 15] Voorbeeld opslaan in /output? (j/n) [n]: "
if /i "%S_PREV%"=="j" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [FOUT] Conversie mislukt. ) else ( color 0A & echo [SUCCES] Bestanden gegenereerd. )

echo.
set /p "AGAIN=Nog een afbeelding converteren? (j/n): "
if /i "%AGAIN%"=="j" goto START
cd scripts
exit /b