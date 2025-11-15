@echo off

for %%f in ("map.pkb_OUT\*.dap") do (
	mkdir "%%f"
	quickbms.exe -d "dap_map.bms" "%%f" ""
)

pause