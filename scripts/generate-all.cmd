@echo off
REM scripts\generate-all.cmd
REM For each grammar in this repo:
REM   1. Rebuild grammar.json from the Python generator.
REM   2. Rebuild parser.c from grammar.json.
REM   3. Stage grammar.json into src\ (required by `tree-sitter build`).
REM   4. Build the shared library.

setlocal
set ROOT=%~dp0..
set TS=%ROOT%\tree-sitter.exe

if not exist "%TS%" (
    echo ERROR: tree-sitter.exe not found at %TS%
    exit /b 1
)

for %%G in (lsl slua) do (
    if exist "%ROOT%\%%G\generate_%%G_grammar.py" (
        pushd "%ROOT%\%%G"

        echo === Generating grammar.json for %%G ===
        python generate_%%G_grammar.py
        if errorlevel 1 (
            popd
            echo ERROR: Python generator failed for %%G
            exit /b 1
        )

        echo === Generating parser.c for %%G ===
        "%TS%" generate grammar.json
        if errorlevel 1 (
            popd
            echo ERROR: tree-sitter generate failed for %%G
            exit /b 1
        )

        echo === Staging grammar.json into src\ for %%G ===
        copy /Y grammar.json src\grammar.json >nul
        if errorlevel 1 (
            popd
            echo ERROR: could not copy grammar.json into src\ for %%G
            exit /b 1
        )

        echo === Building %%G shared library ===
        "%TS%" build --output %%G.dll .
        if errorlevel 1 (
            popd
            echo ERROR: build failed for %%G
            exit /b 1
        )

        popd
    ) else (
        echo Skipping %%G ^(no generate_%%G_grammar.py yet^)
    )
)

echo All grammars generated and built.
endlocal