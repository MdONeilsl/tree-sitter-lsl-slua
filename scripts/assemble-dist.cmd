@echo off
REM scripts\assemble-dist.cmd
REM
REM Assemble a drop-in release folder under dist\:
REM
REM   dist\CMakeLists.txt                  FetchContent-ready root
REM   dist\lsl\CMakeLists.txt              per-grammar wrapper
REM   dist\lsl\include\lsl.h               public header
REM   dist\lsl\src\parser.c                generated C source
REM   dist\lsl\src\tree_sitter\parser.h    internal header
REM   dist\lsl\lsl.dll                     runtime library (Windows)
REM   dist\slua\...                        same layout for SLua
REM   dist\README.md                       usage documentation
REM
REM The tree-sitter RUNTIME is NOT shipped. Consumers supply it via
REM find_package(tree-sitter), vcpkg, apt, brew, or tree-sitter_ROOT.

setlocal EnableDelayedExpansion
set ROOT=%~dp0..
set DIST=%ROOT%\dist

REM ---- Sanity checks -------------------------------------------------------
if not exist "%ROOT%\CMakeLists.txt" (
    echo ERROR: root CMakeLists.txt missing.
    exit /b 1
)
if not exist "%ROOT%\lsl\src\parser.c" (
    echo ERROR: lsl\src\parser.c missing. Run scripts\generate-all.cmd first.
    exit /b 1
)
if not exist "%ROOT%\lsl\lsl.dll" (
    echo ERROR: lsl\lsl.dll missing. Run scripts\generate-all.cmd first.
    exit /b 1
)

REM ---- Rebuild dist\ -------------------------------------------------------
echo === Cleaning %DIST% ===
if exist "%DIST%" rmdir /s /q "%DIST%"

echo === Creating layout ===
mkdir "%DIST%"                                     || goto :fail
mkdir "%DIST%\lsl\include"                         || goto :fail
mkdir "%DIST%\lsl\src\tree_sitter"                 || goto :fail

echo === Copying root CMakeLists.txt ===
copy /Y "%ROOT%\CMakeLists.txt" "%DIST%\CMakeLists.txt" >nul || goto :fail

echo === Copying LSL artifacts ===
copy /Y "%ROOT%\lsl\CMakeLists.txt"                  "%DIST%\lsl\CMakeLists.txt"                  >nul || goto :fail
copy /Y "%ROOT%\lsl\include\lsl.h"                   "%DIST%\lsl\include\lsl.h"                   >nul || goto :fail
copy /Y "%ROOT%\lsl\src\parser.c"                    "%DIST%\lsl\src\parser.c"                    >nul || goto :fail
copy /Y "%ROOT%\lsl\src\tree_sitter\parser.h"        "%DIST%\lsl\src\tree_sitter\parser.h"        >nul || goto :fail
copy /Y "%ROOT%\lsl\lsl.dll"                         "%DIST%\lsl\lsl.dll"                         >nul || goto :fail

REM ---- SLua (enable when the grammar exists) ------------------------------
if exist "%ROOT%\slua\src\parser.c" (
    echo === Copying SLua artifacts ===
    mkdir "%DIST%\slua\include"                    || goto :fail
    mkdir "%DIST%\slua\src\tree_sitter"            || goto :fail
    copy /Y "%ROOT%\slua\CMakeLists.txt"             "%DIST%\slua\CMakeLists.txt"             >nul || goto :fail
    copy /Y "%ROOT%\slua\include\slua.h"             "%DIST%\slua\include\slua.h"             >nul || goto :fail
    copy /Y "%ROOT%\slua\src\parser.c"               "%DIST%\slua\src\parser.c"               >nul || goto :fail
    copy /Y "%ROOT%\slua\src\tree_sitter\parser.h"   "%DIST%\slua\src\tree_sitter\parser.h"   >nul || goto :fail
    copy /Y "%ROOT%\slua\slua.dll"                   "%DIST%\slua\slua.dll"                   >nul || goto :fail
) else (
    echo NOTE: slua\src\parser.c not found; SLua omitted from dist.
)

echo === Copying README ===
if exist "%ROOT%\packaging\README.md" (
    copy /Y "%ROOT%\packaging\README.md" "%DIST%\README.md" >nul || goto :fail
)

echo.
echo Package assembled at: %DIST%
endlocal
exit /b 0

:fail
echo ERROR: dist assembly failed.
endlocal
exit /b 1