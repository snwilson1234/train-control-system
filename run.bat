@ECHO OFF
cls
echo COPYING FILES
xcopy /s /y .\plc_programs\green_line\og_var_files  .\plc_programs\green_line\var_files
xcopy /s /y .\plc_programs\red_line\og_var_files  .\plc_programs\red_line\var_files
echo COPYING COMPLETE
echo RESETTING DATABASE
if exist .\track_model\track.db (
    del .\track_model\track.db
    echo track.db deleted.
) else (
    echo track.db has already been deleted.
)
echo DATABASE RESET
@REM python ./god.py
.\dist\god.exe
