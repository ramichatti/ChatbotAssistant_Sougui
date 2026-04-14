@echo off
title Sougui AI - Assistant IA Professionnel
color 0B
mode con: cols=80 lines=30

echo.
echo ========================================================================
echo.
echo          ███████╗ ██████╗ ██╗   ██╗ ██████╗ ██╗   ██╗██╗
echo          ██╔════╝██╔═══██╗██║   ██║██╔════╝ ██║   ██║██║
echo          ███████╗██║   ██║██║   ██║██║  ███╗██║   ██║██║
echo          ╚════██║██║   ██║██║   ██║██║   ██║██║   ██║██║
echo          ███████║╚██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝██║
echo          ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝
echo.
echo                    ASSISTANT IA PROFESSIONNEL
echo                  Advanced IA System
echo.
echo ========================================================================
echo.
echo  [*] Demarrage de l'application...
echo  [*] Version: 2.0 Advanced
echo  [*] Moteur IA: Ollama llama3.1:latest
echo  [*] Base de donnees: Sougui_DWH
echo.
echo ========================================================================
echo.
echo  IDENTIFIANTS DE CONNEXION:
echo  Username: sougui
echo  Password: sougui
echo.
echo ========================================================================
echo.

REM Verification de Python
py.exe --version >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK] Python detecte
    echo.
    echo  [*] Lancement de Sougui AI...
    echo.
    py.exe main.py
) else (
    python --version >nul 2>&1
    if %errorlevel% == 0 (
        echo  [OK] Python detecte
        echo.
        echo  [*] Lancement de Sougui AI...
        echo.
        python main.py
    ) else (
        echo  [ERREUR] Python n'est pas installe!
        echo.
        echo  Veuillez installer Python 3.8+ depuis python.org
        echo  Ou installez depuis le Microsoft Store
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================================================
echo  Application fermee. Merci d'avoir utilise Sougui AI!
echo ========================================================================
echo.
pause
