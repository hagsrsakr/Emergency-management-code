@echo off
setlocal
cd /d "%~dp0"
call scripts\00_install.bat
if errorlevel 1 exit /b 1

python scripts\01_download_sf_cad.py
if errorlevel 1 exit /b 1
python scripts\02_prepare_real_data.py
if errorlevel 1 exit /b 1
python scripts\03_validate_and_select_models.py
if errorlevel 1 exit /b 1
python scripts\04_build_incident_resource_matrix.py
if errorlevel 1 exit /b 1
python scripts\05_score_pairs_with_ai.py
if errorlevel 1 exit /b 1
python scripts\06_run_shap.py
if errorlevel 1 exit /b 1
python scripts\07_compare_strategies.py
if errorlevel 1 exit /b 1
python scripts\08_statistical_tests.py
if errorlevel 1 exit /b 1
python scripts\09_scalability.py
if errorlevel 1 exit /b 1

streamlit run app.py
