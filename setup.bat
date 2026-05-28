@echo off
setlocal enabledelayedexpansion
title DocumentView - Installer
 
set REPO_URL=https://github.com/DonaldMOUAFO/documentView.git
set PROJECT_DIR=documentView
set OLLAMA_CONTAINER=ollama-server
set STREAMLIT_CONTAINER=documentview
set OLLAMA_MODEL=llama3
set MAX_WAIT=60
 
:: ─────────────────────────────────────────────
::  Colors via PowerShell (works on Win 10/11)
:: ─────────────────────────────────────────────
call :banner
 
:: ─────────────────────────────────────────────
::  1. Preflight checks
:: ─────────────────────────────────────────────
call :info "Checking required tools..."
 
where git >nul 2>&1
if %errorlevel% neq 0 (
    call :error "git is not installed."
    echo     Download it from: https://git-scm.com/download/win
    pause & exit /b 1
)
 
where docker >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Docker is not installed."
    echo     Download Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause & exit /b 1
)
 
docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Docker Desktop is not running."
    echo     Please start Docker Desktop and try again.
    pause & exit /b 1
)
 
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Docker Compose not found. Update Docker Desktop to the latest version."
    pause & exit /b 1
)
 
call :success "All tools are available."
 
:: ─────────────────────────────────────────────
::  2. Clone or update the repository
:: ─────────────────────────────────────────────
if exist "%PROJECT_DIR%\.git" (
    call :warn "Repository already exists. Pulling latest changes..."
    git -C "%PROJECT_DIR%" pull
    if %errorlevel% neq 0 ( call :error "Failed to pull latest changes." & pause & exit /b 1 )
) else (
    call :info "Cloning repository..."
    git clone "%REPO_URL%" "%PROJECT_DIR%"
    if %errorlevel% neq 0 ( call :error "Failed to clone repository." & pause & exit /b 1 )
)
 
call :success "Repository ready."
cd "%PROJECT_DIR%"
 
:: ─────────────────────────────────────────────
::  3. Clean up old containers
:: ─────────────────────────────────────────────
call :info "Cleaning up old containers..."
 
for %%C in (%OLLAMA_CONTAINER% %STREAMLIT_CONTAINER%) do (
    docker ps -a --format "{{.Names}}" | findstr /x "%%C" >nul 2>&1
    if !errorlevel! equ 0 (
        call :warn "Removing existing container: %%C"
        docker rm -f %%C >nul 2>&1
    )
)
 
call :success "Cleanup done."
 
:: ─────────────────────────────────────────────
::  4. Build and start containers
:: ─────────────────────────────────────────────
call :info "Building Docker images (this may take a few minutes)..."
 
docker compose up -d --build
if %errorlevel% neq 0 ( call :error "docker compose up failed." & pause & exit /b 1 )
 
call :success "Containers are running."
 
:: ─────────────────────────────────────────────
::  5. Wait for Ollama to be ready
:: ─────────────────────────────────────────────
call :info "Waiting for Ollama to be ready..."
 
set ELAPSED=0
:wait_loop
    docker exec %OLLAMA_CONTAINER% ollama list >nul 2>&1
    if %errorlevel% equ 0 goto ollama_ready
    if %ELAPSED% geq %MAX_WAIT% (
        call :error "Ollama did not start within %MAX_WAIT%s."
        echo     Check logs with: docker logs %OLLAMA_CONTAINER%
        pause & exit /b 1
    )
    timeout /t 2 /nobreak >nul
    set /a ELAPSED+=2
    goto wait_loop
 
:ollama_ready
call :success "Ollama is ready."
 
:: ─────────────────────────────────────────────
::  6. Pull model if not already present
:: ─────────────────────────────────────────────
call :info "Checking model %OLLAMA_MODEL%..."
 
docker exec %OLLAMA_CONTAINER% ollama list 2>&1 | findstr /i "%OLLAMA_MODEL%" >nul 2>&1
if %errorlevel% equ 0 (
    call :success "Model '%OLLAMA_MODEL%' already present, skipping pull."
) else (
    call :info "Pulling model '%OLLAMA_MODEL%' (may take several minutes depending on your connection)..."
    docker exec -it %OLLAMA_CONTAINER% ollama pull %OLLAMA_MODEL%
    if %errorlevel% neq 0 ( call :error "Failed to pull model." & pause & exit /b 1 )
    call :success "Model '%OLLAMA_MODEL%' ready."
)
 
:: ─────────────────────────────────────────────
::  7. Open the app in the browser
:: ─────────────────────────────────────────────
call :info "Opening the app in your browser..."
timeout /t 2 /nobreak >nul
start http://localhost:8501
 
:: ─────────────────────────────────────────────
::  8. Final summary
:: ─────────────────────────────────────────────
echo.
echo  ==================================================
call :success " Deployment complete!"
echo.
echo    Streamlit app  ^>  http://localhost:8501
echo    Ollama API     ^>  http://localhost:11434
echo    Model          ^>  %OLLAMA_MODEL%
echo.
echo    Useful commands:
echo      docker compose logs -f    (follow logs)
echo      docker compose down       (stop everything)
echo  ==================================================
echo.
pause
exit /b 0
 
:: ─────────────────────────────────────────────
::  Helper subroutines
:: ─────────────────────────────────────────────
:banner
echo.
echo  ****************************************************
echo  *                                                  *
echo  *        DocumentView  --  Installer               *
echo  *                                                  *
echo  ****************************************************
echo.
goto :eof
 
:info
echo [INFO]   %~1
goto :eof
 
:success
echo [OK]     %~1
goto :eof
 
:warn
echo [WARN]   %~1
goto :eof
 
:error
echo.
echo [ERROR]  %~1
echo.
goto :eof
