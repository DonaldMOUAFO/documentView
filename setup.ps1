# ─────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────
$REPO_URL          = "https://github.com/DonaldMOUAFO/documentView.git"
$PROJECT_DIR       = "documentView"
$OLLAMA_CONTAINER  = "ollama-server"
$STREAMLIT_CONTAINER = "documentview"
$OLLAMA_MODEL      = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "llama3" }
$MAX_WAIT          = 60
 
# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
function Info    { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Success { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Warning { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Err     { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }
 
# ─────────────────────────────────────────────
#  1. Preflight checks
# ─────────────────────────────────────────────
Info "Running preflight checks..."
 
if (-not (Get-Command git    -ErrorAction SilentlyContinue)) { Err "git is not installed. Download it from https://git-scm.com" }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Err "Docker is not installed. Download Docker Desktop from https://www.docker.com/products/docker-desktop" }
 
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Err "Docker daemon is not running. Please start Docker Desktop." }
 
docker compose version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Err "Docker Compose not found. It comes bundled with Docker Desktop — make sure it is up to date." }
 
Success "Preflight checks passed."
 
# ─────────────────────────────────────────────
#  2. Clone or update the repository
# ─────────────────────────────────────────────
if (Test-Path "$PROJECT_DIR\.git") {
    Warning "Repository already exists — pulling latest changes..."
    git -C $PROJECT_DIR pull
    if ($LASTEXITCODE -ne 0) { Err "Failed to pull latest changes." }
} else {
    Info "Cloning repository from $REPO_URL..."
    git clone $REPO_URL $PROJECT_DIR
    if ($LASTEXITCODE -ne 0) { Err "Failed to clone repository." }
}
 
Success "Repository ready at .\$PROJECT_DIR"
Set-Location $PROJECT_DIR
 
# ─────────────────────────────────────────────
#  3. Clean up any old containers
# ─────────────────────────────────────────────
Info "Cleaning up existing containers..."
 
foreach ($CONTAINER in @($OLLAMA_CONTAINER, $STREAMLIT_CONTAINER)) {
    $exists = docker ps -a --format "{{.Names}}" | Select-String -Pattern "^$CONTAINER$"
    if ($exists) {
        Warning "Found existing container '$CONTAINER' — removing it..."
        docker rm -f $CONTAINER
        if ($LASTEXITCODE -ne 0) { Err "Could not remove container '$CONTAINER'. Try manually: docker rm -f $CONTAINER" }
    }
}
 
Success "Cleanup done."
 
# ─────────────────────────────────────────────
#  4. Build images and start containers
# ─────────────────────────────────────────────
Info "Building Docker images and starting containers..."
 
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { Err "docker compose up failed." }
 
Success "Containers started."
 
# ─────────────────────────────────────────────
#  5. Wait for Ollama to be ready
# ─────────────────────────────────────────────
Info "Waiting for Ollama to be ready (max ${MAX_WAIT}s)..."
 
$elapsed = 0
while ($true) {
    docker exec $OLLAMA_CONTAINER ollama list 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { break }
    if ($elapsed -ge $MAX_WAIT) { Err "Ollama did not become ready within ${MAX_WAIT}s. Check logs: docker logs $OLLAMA_CONTAINER" }
    Start-Sleep -Seconds 2
    $elapsed += 2
}
 
Success "Ollama is ready."
 
# ─────────────────────────────────────────────
#  6. Pull the model if not already present
# ─────────────────────────────────────────────
Info "Checking if model '$OLLAMA_MODEL' is already pulled..."
 
$modelExists = docker exec $OLLAMA_CONTAINER ollama list 2>&1 | Select-String -Pattern $OLLAMA_MODEL
if ($modelExists) {
    Success "Model '$OLLAMA_MODEL' already present, skipping pull."
} else {
    Info "Pulling model '$OLLAMA_MODEL' (this may take a while)..."
    docker exec -it $OLLAMA_CONTAINER ollama pull $OLLAMA_MODEL
    if ($LASTEXITCODE -ne 0) { Err "Failed to pull model '$OLLAMA_MODEL'." }
    Success "Model '$OLLAMA_MODEL' pulled."
}
 
# ─────────────────────────────────────────────
#  7. Final status
# ─────────────────────────────────────────────
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Success "Deployment complete!"
Write-Host ""
Write-Host "  Streamlit app : http://localhost:8501"
Write-Host "  Ollama API    : http://localhost:11434"
Write-Host "  Model         : $OLLAMA_MODEL"
Write-Host "  Project dir   : $(Get-Location)"
Write-Host ""
Write-Host "  Useful commands:"
Write-Host "    docker compose logs -f                          # follow logs"
Write-Host "    docker compose down                             # stop everything"
Write-Host "    docker exec -it $OLLAMA_CONTAINER ollama list  # list models"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green