@echo off

echo ================================
echo FraudLens Demo
echo ================================

cd /d "%~dp0.."

python scripts\generate_transactions.py

echo.
echo Demo data generated.
pause