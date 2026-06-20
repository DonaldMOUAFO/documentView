#!/bin/bash
set -e


# ─────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────
# Define the directory where the script is located
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPO_URL="https://github.com/DonaldMOUAFO/documentView.git"
PROJECT_DIR="documentView"
OLLAMA_CONTAINER="ollama-server"
STREAMLIT_CONTAINER="documentview"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"
MAX_WAIT=60

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
info()    { echo -e "\033[1;34m[INFO]\033[0m  $*"; }
success() { echo -e "\033[1;32m[OK]\033[0m    $*"; }
warning() { echo -e "\033[1;33m[WARN]\033[0m  $*"; }
error()   { echo -e "\033[1;31m[ERROR]\033[0m $*"; exit 1; }

# ─────────────────────────────────────────────
#  1. Preflight checks
# ─────────────────────────────────────────────
info "Running preflight checks..."
 
command -v git    &>/dev/null || error "git is not installed. Run: sudo apt install git"
command -v docker &>/dev/null || error "Docker is not installed or not in PATH."
docker info       &>/dev/null || error "Docker daemon is not running. Start it with: sudo systemctl start docker"
docker compose version &>/dev/null || error "Docker Compose plugin not found. Run: sudo apt install docker-compose-plugin"
 
success "Preflight checks passed."

# ─────────────────────────────────────────────
#  2. Clone or update the repository
# ─────────────────────────────────────────────
if [ -d "$PROJECT_DIR/.git" ]; then
  warning "Repository already exists — pulling latest changes..."
  git -C "$PROJECT_DIR" pull || error "Failed to pull latest changes."
else
  info "Cloning repository from $REPO_URL..."
  git clone "$REPO_URL" "$PROJECT_DIR" || error "Failed to clone repository."
fi
 
success "Repository ready at ./$PROJECT_DIR"
 
# Move into the project
cd "$PROJECT_DIR"

# ─────────────────────────────────────────────
#  3. Clean up any stuck/old containers
# ─────────────────────────────────────────────
info "Cleaning up existing containers..."
 
for CONTAINER in "$OLLAMA_CONTAINER" "$STREAMLIT_CONTAINER"; do
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    warning "Found existing container '$CONTAINER' — removing it..."
    docker rm -f "$CONTAINER" 2>/dev/null || {
      warning "Permission denied, retrying with sudo..."
      sudo docker rm -f "$CONTAINER" || error "Could not remove '$CONTAINER'. Try manually: sudo docker rm -f $CONTAINER"
    }
  fi
done
 
success "Cleanup done."

# ─────────────────────────────────────────────
#  4. Build images and start containers
# ─────────────────────────────────────────────
info "Building Docker images and starting containers..."
 
docker compose up -d --build || error "docker compose up failed."
 
success "Containers started."

─────────────────────────────────────────────
#  5. Wait for Ollama to be ready
# ─────────────────────────────────────────────
info "Waiting for Ollama to be ready (max ${MAX_WAIT}s)..."
 
ELAPSED=0
until docker exec "$OLLAMA_CONTAINER" ollama list &>/dev/null; do
  if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    error "Ollama did not become ready within ${MAX_WAIT}s. Check logs: docker logs $OLLAMA_CONTAINER"
  fi
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done
 
success "Ollama is ready."

# ─────────────────────────────────────────────
#  6. Pull the model if not already present
# ─────────────────────────────────────────────
info "Checking if model '$OLLAMA_MODEL' is already pulled..."
 
if docker exec "$OLLAMA_CONTAINER" ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
  success "Model '$OLLAMA_MODEL' already present, skipping pull."
else
  info "Pulling model '$OLLAMA_MODEL' (this may take a while)..."
  docker exec -it "$OLLAMA_CONTAINER" ollama pull "$OLLAMA_MODEL" || error "Failed to pull model '$OLLAMA_MODEL'."
  success "Model '$OLLAMA_MODEL' pulled."
fi

# ─────────────────────────────────────────────
#  7. Final status
# ─────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Deployment complete!"
echo ""
echo "  🌐 Streamlit app : http://localhost:8501"
echo "  🤖 Ollama API    : http://localhost:11434"
echo "  📦 Model         : $OLLAMA_MODEL"
echo "  📁 Project dir   : $(pwd)"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f        # follow logs"
echo "    docker compose down           # stop everything"
echo "    docker exec -it $OLLAMA_CONTAINER ollama list  # list models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"