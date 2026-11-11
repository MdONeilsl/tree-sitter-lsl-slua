@echo off
REM scripts\assemble-dist.cmd
REM
REM Assemble the drop-in release folder under dist\.
REM
REM Each grammar folder under dist\ is self-contained:
REM   - compile src\parser.c (plus src\scanner.c for SLua) and link the runtime
REM   - or load <grammar>.dll at runtime
REM Nothing outside the grammar folder is needed.
REM
REM The tree-sitter RUNTIME is NOT shipped; consumers install it separately.

setlocal EnableDelayedExpansion
set ROOT=%~dp0..
set DIST=%ROOT%\dist

REM ---- Required top-level files --------------------------------------
if not exist "%ROOT%\CMakeLists.txt" (
    echo ERROR: missing "%ROOT%\CMakeLists.txt"
    exit /b 1
)
if not exist "%ROOT%\README.md" (
    echo ERROR: missing "%ROOT%\README.md"
    exit /b 1
)

REM ---- Required LSL files --------------------------------------------
for %%F in (
    "%ROOT%\lsl\CMakeLists.txt"
    "%ROOT%\lsl\include\lsl.h"
    "%ROOT%\lsl\src\parser.c"
    "%ROOT%\lsl\src\node-types.json"
    "%ROOT%\lsl\src\tree_sitter\parser.h"
    "%ROOT%\lsl\lsl.dll"
) do (
    if not exist %%F (
        echo ERROR: missing %%F
        exit /b 1
    )
)

REM ---- Required SLua files (scanner.c is NOT optional) ---------------
for %%F in (
    "%ROOT%\slua\CMakeLists.txt"
    "%ROOT%\slua\include\slua.h"
    "%ROOT%\slua\src\parser.c"
    "%ROOT%\slua\src\scanner.c"
    "%ROOT%\slua\src\node-types.json"
    "%ROOT%\slua\src\tree_sitter\parser.h"
    "%ROOT%\slua\slua.dll"
) do (
    if not exist %%F (
        echo ERROR: missing %%F
        exit /b 1
    )
)

REM ---- Rebuild dist\ -------------------------------------------------
echo === Cleaning %DIST% ===
if exist "%DIST%" rmdir /s /q "%DIST%"

echo === Creating layout ===
mkdir "%DIST%"                              || goto :fail
mkdir "%DIST%\lsl\include"                  || goto :fail
mkdir "%DIST%\lsl\src\tree_sitter"          || goto :fail
mkdir "%DIST%\slua\include"                 || goto :fail
mkdir "%DIST%\slua\src\tree_sitter"         || goto :fail

echo === Copying root files ===
copy /Y "%ROOT%\CMakeLists.txt"                 "%DIST%\CMakeLists.txt"                 >nul || goto :fail
copy /Y "%ROOT%\README.md"                      "%DIST%\README.md"                      >nul || goto :fail
if exist "%ROOT%\LICENSE" (
    copy /Y "%ROOT%\LICENSE"                    "%DIST%\LICENSE"                        >nul || goto :fail
)
if exist "%ROOT%\THIRD_PARTY_NOTICES.md" (
    copy /Y "%ROOT%\THIRD_PARTY_NOTICES.md"     "%DIST%\THIRD_PARTY_NOTICES.md"         >nul || goto :fail
)

echo === Copying LSL ===
copy /Y "%ROOT%\lsl\CMakeLists.txt"             "%DIST%\lsl\CMakeLists.txt"             >nul || goto :fail
copy /Y "%ROOT%\lsl\include\lsl.h"              "%DIST%\lsl\include\lsl.h"              >nul || goto :fail
copy /Y "%ROOT%\lsl\src\parser.c"               "%DIST%\lsl\src\parser.c"               >nul || goto :fail
copy /Y "%ROOT%\lsl\src\node-types.json"        "%DIST%\lsl\src\node-types.json"        >nul || goto :fail
copy /Y "%ROOT%\lsl\src\tree_sitter\parser.h"   "%DIST%\lsl\src\tree_sitter\parser.h"   >nul || goto :fail
copy /Y "%ROOT%\lsl\lsl.dll"                    "%DIST%\lsl\lsl.dll"                    >nul || goto :fail
if exist "%ROOT%\lsl\src\grammar.json" (
    copy /Y "%ROOT%\lsl\src\grammar.json"       "%DIST%\lsl\src\grammar.json"           >nul || goto :fail
)

echo === Copying SLua ===
copy /Y "%ROOT%\slua\CMakeLists.txt"            "%DIST%\slua\CMakeLists.txt"            >nul || goto :fail
copy /Y "%ROOT%\slua\include\slua.h"            "%DIST%\slua\include\slua.h"            >nul || goto :fail
copy /Y "%ROOT%\slua\src\parser.c"              "%DIST%\slua\src\parser.c"              >nul || goto :fail
copy /Y "%ROOT%\slua\src\scanner.c"             "%DIST%\slua\src\scanner.c"             >nul || goto :fail
copy /Y "%ROOT%\slua\src\node-types.json"       "%DIST%\slua\src\node-types.json"       >nul || goto :fail
copy /Y "%ROOT%\slua\src\tree_sitter\parser.h"  "%DIST%\slua\src\tree_sitter\parser.h"  >nul || goto :fail
copy /Y "%ROOT%\slua\slua.dll"                  "%DIST%\slua\slua.dll"                  >nul || goto :fail
if exist "%ROOT%\slua\src\grammar.json" (
    copy /Y "%ROOT%\slua\src\grammar.json"      "%DIST%\slua\src\grammar.json"          >nul || goto :fail
)

echo.
echo Package assembled at: %DIST%
endlocal
exit /b 0

:fail
echo ERROR: dist assembly failed.
endlocal
exit /b 1