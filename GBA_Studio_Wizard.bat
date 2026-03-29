@echo off
setlocal enabledelayedexpansion
title GBA Background Studio - Language Selection
color 0F

:MENU
cls
echo ======================================================
echo       GBA BACKGROUND STUDIO - SELECT LANGUAGE
echo ======================================================
echo.
echo  1. English             10. Polski
echo  2. Espanol             11. Tieng Viet
echo  3. Portugues (BR)      12. Bahasa Indonesia
echo  4. Francais            13. Hindi (EN Interface)
echo  5. Deutsch             14. Russian (EN Interface)
echo  6. Italiano            15. Japanese (EN Interface)
echo  7. Portugues           16. Chinese Simp. (EN Interface)
echo  8. Nederlands          17. Chinese Trad. (EN Interface)
echo  9. Turkce              18. Korean (EN Interface)
echo.
echo  0. Exit
echo.
set /p "L=Choice [1-18]: "

if "%L%"=="1"  call "scripts\convert_eng.bat"
if "%L%"=="2"  call "scripts\convert_spa.bat"
if "%L%"=="3"  call "scripts\convert_brp.bat"
if "%L%"=="4"  call "scripts\convert_fra.bat"
if "%L%"=="5"  call "scripts\convert_deu.bat"
if "%L%"=="6"  call "scripts\convert_ita.bat"
if "%L%"=="7"  call "scripts\convert_por.bat"
if "%L%"=="8"  call "scripts\convert_nld.bat"
if "%L%"=="9"  call "scripts\convert_tur.bat"
if "%L%"=="10" call "scripts\convert_pol.bat"
if "%L%"=="11" call "scripts\convert_vie.bat"
if "%L%"=="12" call "scripts\convert_ind.bat"
if "%L%"=="13" call "scripts\convert_eng.bat"
if "%L%"=="14" call "scripts\convert_eng.bat"
if "%L%"=="15" call "scripts\convert_eng.bat"
if "%L%"=="16" call "scripts\convert_eng.bat"
if "%L%"=="17" call "scripts\convert_eng.bat"
if "%L%"=="18" call "scripts\convert_eng.bat"

if "%L%"=="0" exit
goto MENU
