@echo off

for %%f in ("common.pkb_OUT\*.dat") do (
	mkdir "%%f"
	quickbms.exe -d "xenoblade bdat.bms" "%%f" ""
)

pause