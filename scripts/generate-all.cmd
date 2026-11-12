@echo off
REM scripts\generate-all.cmd
REM
REM Windows counterpart to scripts/generate-all.sh.
REM Auto-downloads the tree-sitter CLI if not present at the repo root,
REM then regenerates grammar.json, parser.c, and the shared library
REM for each grammar.

setlocal EnableDelayedExpansion
set ROOT=%~dp0..
set TS=%ROOT%\tree-sitter.exe

REM ------------------------------------------------------------------
REM Download CLI if missing.  No paren blocks here — top-level gotos
REM avoid a class of cmd parse-time bugs where `set VAR=...` inside a
REM nested if/else block can leave VAR empty.
REM ------------------------------------------------------------------
if exist "%TS%" goto :have_cli

set CLI_VERSION=0.27.2
set CLI_ARCH=windows-x64
if /I "%PROCESSOR_ARCHITECTURE%"=="ARM64" set CLI_ARCH=windows-arm64

set CLI_URL=https://github.com/tree-sitter/tree-sitter/releases/download/v%CLI_VERSION%/tree-sitter-cli-%CLI_ARCH%.zip

echo === Downloading tree-sitter CLI %CLI_VERSION% (%CLI_ARCH%) ===
echo URL: %CLI_URL%

powershell -NoProfile -Command "Invoke-WebRequest -Uri '%CLI_URL%' -OutFile '%TEMP%\ts-cli.zip'"
if errorlevel 1 (
    echo ERROR: could not download the tree-sitter CLI.
    exit /b 1
)

powershell -NoProfile -Command "Expand-Archive -Path '%TEMP%\ts-cli.zip' -DestinationPath '%TEMP%\ts-cli' -Force"
if errorlevel 1 (
    echo ERROR: could not expand the tree-sitter CLI archive.
    exit /b 1
)

copy /Y "%TEMP%\ts-cli\tree-sitter.exe" "%TS%" >nul
del "%TEMP%\ts-cli.zip" 2>nul
rmdir /s /q "%TEMP%\ts-cli" 2>nul

if not exist "%TS%" (
    echo ERROR: tree-sitter.exe not found after extraction.
    exit /b 1
)

:have_cli

echo === tree-sitter version ===
"%TS%" --version

REM ------------------------------------------------------------------
REM Generate and build each grammar.
REM ------------------------------------------------------------------
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