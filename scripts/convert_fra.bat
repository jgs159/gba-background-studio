@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set PYTHONPATH=%CD%

:START
cls
color 0F
echo ======================================================
echo       GBA BACKGROUND STUDIO - ASSISTANT (FR)
echo ======================================================
echo.

:GET_IMG
set "INPUT_IMG="
echo [ETAPE 1]
set /p "INPUT_IMG=Glissez l'image (PNG/BMP) et appuyez sur Entree: "
if not defined INPUT_IMG goto GET_IMG
set "INPUT_IMG=%INPUT_IMG:"=%"
if not exist "%INPUT_IMG%" (
    echo [ERREUR] Fichier non trouve.
    goto GET_IMG
)

:GET_MODE
echo.
echo [ETAPE 2] Choisissez le Mode GBA:
echo     1. Mode Texte (Standard)
echo     2. Rotation/Zoom (Affine)
set "MODE_CHOICE=1"
set /p "MODE_CHOICE=Choix [1-2] (Defaut: 1): "
if "%MODE_CHOICE%"=="1" (set "ROT_ARG=" & goto GET_BPP)
if "%MODE_CHOICE%"=="2" (set "ROT_ARG=--rotation-mode" & set "BPP_VAL=8" & goto GET_8BPP)
echo [ERREUR] Option invalide. & goto GET_MODE

:GET_BPP
echo.
echo [ETAPE 3] Bits Par Pixel (BPP):
echo     1. 4bpp (16 couleurs par palette)
echo     2. 8bpp (256 couleurs au total)
set "BPP_CHOICE=1"
set /p "BPP_CHOICE=Choix [1-2] (Defaut: 1): "
if "%BPP_CHOICE%"=="1" (set "BPP_VAL=4" & goto GET_4BPP)
if "%BPP_CHOICE%"=="2" (set "BPP_VAL=8" & goto GET_8BPP)
echo [ERREUR] Option invalide. & goto GET_BPP

:GET_4BPP
echo.
echo [ETAPE 4] Configuration 4bpp:
echo     1. Utiliser des Slots de Palette personnalises
echo     2. Utiliser un Tilemap existant (.bin)
set "TYPE_4BPP=1"
set /p "TYPE_4BPP=Choix [1-2] (Defaut: 1): "
if "%TYPE_4BPP%"=="1" goto GET_PALS
if "%TYPE_4BPP%"=="2" (
    set /p "TMAP_PATH=   Glissez le fichier .bin ici: "
    set "TMAP_ARG=--tilemap "!TMAP_PATH:"=!""
    goto COMMON
)
goto GET_4BPP

:GET_PALS
echo.
set "PALS=0"
set /p "PALS=[ETAPE 5] Slots de palette (ex: 0,1,2) [Defaut: 0]: "
set "PALS_ARG=--selected-palettes "%PALS%""
goto COMMON

:GET_8BPP
echo.
set "START_IDX=0"
set /p "START_IDX=[ETAPE 5] Index de couleur de depart (0-255) [Defaut: 0]: "
set "PAL_SIZE=256"
set /p "PAL_SIZE=[ETAPE 6] Nombre de couleurs (1-256) [Defaut: 256]: "
set "B8_ARGS=--start-index %START_IDX% --palette-size %PAL_SIZE%"
goto COMMON

:COMMON
echo.
set "TRANS_CLR=0,0,0"
set /p "TRANS_CLR=[ETAPE 7] Couleur Transparente (R,G,B) [Defaut: 0,0,0]: "
set "C_ARGS=--transparent-color "%TRANS_CLR%""

set "KEEP_T=n"
set /p "KEEP_T=[ETAPE 8] Garder la couleur transparente dans la palette? (o/n) [n]: "
if /i "%KEEP_T%"=="o" set "C_ARGS=!C_ARGS! --keep-transparent"

echo.
set "EXT_T=0"
set /p "EXT_T=[ETAPE 9] Tuiles transparentes supplementaires au debut [Defaut: 0]: "
set "C_ARGS=!C_ARGS! --extra-transparent-tiles %EXT_T%"

set "TS_W="
set /p "TS_W=[ETAPE 10] Forcer la largeur du Tileset (1-64) [Defaut: auto]: "
if defined TS_W set "C_ARGS=!C_ARGS! --tileset-width %TS_W%"

echo.
set "ORIG="
set /p "ORIG=[ETAPE 11] Origine du recadrage (ex: 1t,1t ou 8,8) [Defaut: 0,0]: "
if defined ORIG set "C_ARGS=!C_ARGS! --origin "%ORIG%""

set "C_END="
set /p "C_END=[ETAPE 12] Fin du recadrage (ex: 30t,18t) [Optionnel]: "
if defined C_END set "C_ARGS=!C_ARGS! --end "%C_END%""

echo.
set "OUT_S="
set /p "OUT_S=[ETAPE 13] Taille de sortie (screen, bg0, 32t,20t) [Defaut: Original]: "
if defined OUT_S set "C_ARGS=!C_ARGS! --output-size "%OUT_S%""

echo.
set "K_TEMP=n"
set /p "K_TEMP=[ETAPE 14] Garder les fichiers temporaires? (o/n) [n]: "
if /i "%K_TEMP%"=="o" (set "EXT_OPTS=--keep-temp") else (set "EXT_OPTS=")

set "S_PREV=n"
set /p "S_PREV=[ETAPE 15] Enregistrer l'apercu dans /output? (o/n) [n]: "
if /i "%S_PREV%"=="o" set "EXT_OPTS=!EXT_OPTS! --save-preview"

cls
color 0B
python -m core.main "%INPUT_IMG%" %ROT_ARG% --bpp %BPP_VAL% %PALS_ARG% %TMAP_ARG% %B8_ARGS% %C_ARGS% %EXT_OPTS%

if %ERRORLEVEL% NEQ 0 ( color 0C & echo [ERREUR] La conversion a echoue. ) else ( color 0A & echo [SUCCES] Fichiers generes. )

echo.
set /p "AGAIN=Convertir une autre image? (o/n): "
if /i "%AGAIN%"=="o" goto START
cd scripts
exit /b