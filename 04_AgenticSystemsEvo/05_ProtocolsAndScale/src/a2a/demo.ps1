<#
.SYNOPSIS
    One-shot A2A demo.  Starts the server, waits for it, fetches the
    agent card, runs the client, shuts down cleanly.

.DESCRIPTION
    Sequence:
      1. Launch step_g_agent_server.py in a background job.
      2. Poll /.well-known/agent-card.json until it responds (max 15s).
      3. Print the agent card (formatted).
      4. Run step_h_agent_client.py with a demo prompt.
      5. Stop the server.

    Use this for a live talk when you want ONE command that shows the
    whole A2A story end-to-end without juggling terminals.

.EXAMPLE
    .\demo.ps1
    .\demo.ps1 "What is 43177 times 14694?"
#>

param(
    [string] $UserPrompt = "How many kilometres are 3 miles?"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$server    = Join-Path $scriptDir "step_g_agent_server.py"
$client    = Join-Path $scriptDir "step_h_agent_client.py"
$serverUrl = "http://localhost:8000"
$cardUrl   = "$serverUrl/.well-known/agent-card.json"

function Section($title) {
    Write-Host ""
    Write-Host ("═" * 70) -ForegroundColor DarkGray
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host ("═" * 70) -ForegroundColor DarkGray
}


# ── 1. launch server in a background job ──────────────────────────────
Section "1/4  starting A2A server (background)"
Write-Host "→ python $server"

$job = Start-Job -ScriptBlock {
    param($py)
    & python $py
} -ArgumentList $server

# ── 2. wait until the card endpoint responds ──────────────────────────
Section "2/4  waiting for server to accept requests"

$deadline = (Get-Date).AddSeconds(15)
$ready = $false
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest -Uri $cardUrl -TimeoutSec 2 -UseBasicParsing
        $ready = $true
        break
    } catch {
        Start-Sleep -Milliseconds 400
    }
}

if (-not $ready) {
    Write-Host "[error] server did not respond within 15 s" -ForegroundColor Red
    Receive-Job $job
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "→ server up at $serverUrl" -ForegroundColor Green


# ── 3. fetch and pretty-print the agent card ──────────────────────────
Section "3/4  GET  $cardUrl"

try {
    $cardJson = Invoke-RestMethod -Uri $cardUrl -TimeoutSec 10
    $cardJson | ConvertTo-Json -Depth 8
} catch {
    Write-Host "[warn] failed to fetch card: $_" -ForegroundColor Yellow
}


# ── 4. run the client script ──────────────────────────────────────────
Section "4/4  python step_h_agent_client.py `"$UserPrompt`""

try {
    & python $client $UserPrompt
    $clientExit = $LASTEXITCODE
} catch {
    Write-Host "[warn] client raised: $_" -ForegroundColor Yellow
    $clientExit = 1
}


# ── 5. shutdown ───────────────────────────────────────────────────────
Section "shutdown"

Stop-Job $job -ErrorAction SilentlyContinue | Out-Null
$serverOutput = Receive-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue

if ($serverOutput) {
    Write-Host "── server log ─────────────────────────────" -ForegroundColor DarkGray
    $serverOutput | ForEach-Object { Write-Host $_ -ForegroundColor DarkGray }
}

Write-Host ""
if ($clientExit -eq 0) {
    Write-Host "✓ demo complete" -ForegroundColor Green
} else {
    Write-Host "✗ demo finished with errors (exit $clientExit)" -ForegroundColor Yellow
}
exit $clientExit