param (
    [ValidateSet("live-build", "debootstrap", "repack")]
    [string]$Engine = "live-build"
)

# ==============================================================================
# Jarvis OS: Multi-Engine Docker ISO Builder (PowerShell for Windows)
# Supports:
#   1. live-build  (Debian Live standard declarative pipeline)
#   2. debootstrap (Minimal transparent chroot & squashfs pipeline)
#   3. repack      (Rapid sub-2-minute in-place ISO patcher)
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "        JARVIS OS (DEBIAN EDITION) ISO BUILD HARNESS      " -ForegroundColor Cyan
Write-Host "        Selected Build Engine: $Engine                    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check if Docker is installed and running
try {
    docker info | Out-Null
    Write-Host "[INFO] Docker daemon detected and responsive." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running or not found. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptDir\..").FullName
$MountPath = $ProjectRoot -replace '\\', '/'
$OutDir = "$ScriptDir\out"

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

# 2. Build the builder image
Write-Host "[INFO] Building Debian live-build container image (jarvis-os-builder)..." -ForegroundColor Yellow
docker build -t jarvis-os-builder -f "$ScriptDir\Dockerfile.builder" "$ScriptDir"

# 3. Select target runner script based on engine
$TargetScript = switch ($Engine) {
    "live-build"  { "/workspace/iso-builder/build-debian-iso.sh" }
    "debootstrap" { "/workspace/iso-builder/build-debootstrap-iso.sh" }
    "repack"      { "/workspace/iso-builder/repack-iso.sh" }
}

Write-Host "[INFO] Launching $Engine pipeline in privileged container ($TargetScript)..." -ForegroundColor Yellow
docker run --rm --privileged `
    -v "${MountPath}:/workspace" `
    -w /workspace/iso-builder `
    jarvis-os-builder `
    /bin/bash $TargetScript

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [INFO] Build process completed. Check output directory:" -ForegroundColor Green
Write-Host " Location: $OutDir" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
