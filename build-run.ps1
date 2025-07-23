# PowerShell version of build-run.sh
$ErrorActionPreference = "Stop"

# 1. Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)\s*=\s*(.+)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim('"')
        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Start PostgreSQL Docker container
Write-Host "Starting PostgreSQL Docker container..."

# Stop and remove existing container if it exists
$containerExists = docker ps -a --format 'table {{.Names}}' | Select-String -Pattern 'postgres-todo'
if ($containerExists) {
    Write-Host "Stopping and removing existing postgres-todo container..."
    docker stop postgres-todo
    docker rm postgres-todo
}

$containerExists = docker ps -a --format 'table {{.Names}}' | Select-String -Pattern 'postgres-todo-test'
if ($containerExists) {
    Write-Host "Stopping and removing existing postgres-todo-test container..."
    docker stop postgres-todo-test
    docker rm postgres-todo-test
}

docker run -d `
    --name postgres-todo `
    -e POSTGRES_DB=$env:DATABASE_NAME `
    -e POSTGRES_USER=$env:DATABASE_USER `
    -e POSTGRES_PASSWORD=$env:DATABASE_PASSWORD `
    -p $env:DATABASE_PORT`:5432 `
    postgres:15

docker run -d `
    --name postgres-todo-test `
    -e POSTGRES_DB=$env:DATABASE_NAME `
    -e POSTGRES_USER=$env:DATABASE_USER `
    -e POSTGRES_PASSWORD=$env:DATABASE_PASSWORD `
    -p 6000:5432 `
    postgres:15

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 2

# Check if PostgreSQL is ready
while ($true) {
    $ready = docker exec postgres-todo pg_isready -U $env:DATABASE_USER -d $env:DATABASE_NAME
    if ($ready -match "accepting connections") {
        break
    }
    Write-Host "Waiting for PostgreSQL to start..."
    Start-Sleep -Seconds 2
}
while ($true) {
    $ready = docker exec postgres-todo-test pg_isready -U $env:DATABASE_USER -d $env:DATABASE_NAME
    if ($ready -match "accepting connections") {
        break
    }
    Write-Host "Waiting for PostgreSQL to start..."
    Start-Sleep -Seconds 2
}


Write-Host "PostgreSQL is ready!"

# run activate
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..."
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Please create it first."
    exit 1
}

# Run Alembic migrations
Write-Host "Running Alembic migrations..."
Write-Host "Applying database migrations..."
alembic upgrade head -x url=$env:DATABASE_URL_ALEMBIC
alembic upgrade head -x url=$env:TEST_DATABASE_URL_ALEMBIC
Write-Host "Database migrations completed successfully!"

uv run run.py
Write-Host "Setup completed successfully!"
