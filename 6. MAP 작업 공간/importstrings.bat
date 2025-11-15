@echo off

for %%f in ("bdat translate\*.txt") do (
    set "name=%%~nf"
    call BdatTool.exe importstrings "bdat_origin\%%~nf.bdat" "%%f" "bdat_output\%%~nf.bdat"
)

pause