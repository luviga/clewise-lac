#!/bin/bash
# Stage 0 solver runs - 2026-11-11 02:20
cd "C:\clw_overnight"

# === CostaRica ===
echo "Running CostaRica BAU_S0..."
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\BAU_S0_0\BAU_S0_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running CostaRica NDCNEW_S0..."
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running CostaRica LTSNEW_S0..."
glpsol -m "CostaRica\CR_ENERGY\t1_confection\OSeMOSYS_Model.txt" -d "CostaRica\CR_ENERGY\t1_confection\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "CostaRica\CR_ENERGY\t1_confection\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

# === DominicanRepublic ===
echo "Running DominicanRepublic BAU_S0..."
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\BAU_S0_0\BAU_S0_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running DominicanRepublic NDCNEW_S0..."
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running DominicanRepublic LTSNEW_S0..."
glpsol -m "DominicanRepublic\RD_ENERGY\OSeMOSYS_Model.txt" -d "DominicanRepublic\RD_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "DominicanRepublic\RD_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

# === Ecuador ===
echo "Running Ecuador BAU_S0..."
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\BAU_S0_0\BAU_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running Ecuador NDCNEW_S0..."
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running Ecuador LTSNEW_S0..."
glpsol -m "Ecuador\ECU_Energy\OSeMOSYS_Model.txt" -d "Ecuador\ECU_Energy\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "Ecuador\ECU_Energy\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

# === Guatemala ===
echo "Running Guatemala BAU_S0..."
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\BAU_S0_0\BAU_S0_0.txt" -o "Guatemala\GUA_ENERGY\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running Guatemala NDCNEW_S0..."
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "Guatemala\GUA_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running Guatemala LTSNEW_S0..."
glpsol -m "Guatemala\GUA_ENERGY\OSeMOSYS_Model.txt" -d "Guatemala\GUA_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "Guatemala\GUA_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

# === Honduras ===
echo "Running Honduras BAU_S0..."
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\BAU_S0_0\BAU_S0_0.txt" -o "Honduras\HON_ENERGY\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running Honduras NDCNEW_S0..."
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "Honduras\HON_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running Honduras LTSNEW_S0..."
glpsol -m "Honduras\HON_ENERGY\OSeMOSYS_Model.txt" -d "Honduras\HON_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "Honduras\HON_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

# === Jamaica ===
echo "Running Jamaica BAU_S0..."
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\BAU_S0_0\BAU_S0_0.txt" -o "Jamaica\JAM_ENERGY\Executables\BAU_S0_0\BAU_S0_0_output.txt"

echo "Running Jamaica NDCNEW_S0..."
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0.txt" -o "Jamaica\JAM_ENERGY\Executables\NDCNEW_S0_0\NDCNEW_S0_0_output.txt"

echo "Running Jamaica LTSNEW_S0..."
glpsol -m "Jamaica\JAM_ENERGY\OSeMOSYS_Model.txt" -d "Jamaica\JAM_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0.txt" -o "Jamaica\JAM_ENERGY\Executables\LTSNEW_S0_0\LTSNEW_S0_0_output.txt"

echo ""
echo "All Stage 0 runs complete!"