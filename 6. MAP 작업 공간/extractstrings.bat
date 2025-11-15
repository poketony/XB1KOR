@echo off

for %%f in ("map.pkb_OUT\*.bdat") do (
    BdatTool.exe exportstrings "%%f" "bdat_translate\%%~nf.txt"
)

pause