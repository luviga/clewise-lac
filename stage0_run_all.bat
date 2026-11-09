@echo off
REM Stage 0 solver runs - 2026-05-14 11:39
cd /d "%~dp0"

REM === Ecuador ===
echo Running Ecuador BAU_S0...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\BAU_S0_0\BAU_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo Running Ecuador NDCNEW_S0...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo Running Ecuador LTSNEW_S0...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

echo.
echo All Stage 0 runs complete!
pause