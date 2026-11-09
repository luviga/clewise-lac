@echo off
REM Stage 3D solver runs - all 18 _FINAL_0 scenarios
cd /d "%~dp0"

REM === CostaRica ===
echo Running CostaRica BAU_FINAL...
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running CostaRica NDCNEW_FINAL...
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running CostaRica LTSNEW_FINAL...
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

REM === DominicanRepublic ===
echo Running DominicanRepublic BAU_FINAL...
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running DominicanRepublic NDCNEW_FINAL...
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running DominicanRepublic LTSNEW_FINAL...
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

REM === Ecuador ===
echo Running Ecuador BAU_FINAL...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "Ecuador\ECU_Energy\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running Ecuador NDCNEW_FINAL...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "Ecuador\ECU_Energy\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running Ecuador LTSNEW_FINAL...
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "Ecuador\ECU_Energy\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

REM === Guatemala ===
echo Running Guatemala BAU_FINAL...
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "Guatemala\GUA_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running Guatemala NDCNEW_FINAL...
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "Guatemala\GUA_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running Guatemala LTSNEW_FINAL...
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "Guatemala\GUA_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

REM === Honduras ===
echo Running Honduras BAU_FINAL...
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "Honduras\HON_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running Honduras NDCNEW_FINAL...
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "Honduras\HON_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running Honduras LTSNEW_FINAL...
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "Honduras\HON_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

REM === Jamaica ===
echo Running Jamaica BAU_FINAL...
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0.txt" -o "Jamaica\JAM_ENERGY\Executables\BAU_FINAL_0\BAU_FINAL_0_output.txt"

echo Running Jamaica NDCNEW_FINAL...
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0.txt" -o "Jamaica\JAM_ENERGY\Executables\NDCNEW_FINAL_0\NDCNEW_FINAL_0_output.txt"

echo Running Jamaica LTSNEW_FINAL...
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0.txt" -o "Jamaica\JAM_ENERGY\Executables\LTSNEW_FINAL_0\LTSNEW_FINAL_0_output.txt"

echo.
echo All 18 Stage 3 FINAL runs complete!
pause
