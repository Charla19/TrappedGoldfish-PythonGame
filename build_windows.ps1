$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$gamePython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $gamePython)) {
    $gamePython = (Get-Command python -ErrorAction Stop).Source
}
$buildEnvironment = Join-Path $projectRoot '.build-venv'
& $gamePython -m venv $buildEnvironment
if ($LASTEXITCODE -ne 0) { throw 'Could not create the build environment.' }
$buildPython = Join-Path $buildEnvironment 'Scripts\python.exe'
& $buildPython -m pip install -r (Join-Path $projectRoot 'requirements-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Could not install the build tools.' }
& $buildPython (Join-Path $projectRoot 'build_windows.py')
if ($LASTEXITCODE -ne 0) { throw 'Could not build the game.' }
Write-Host ('Executable created: ' + (Join-Path $projectRoot 'dist\TrappedGoldfish.exe'))
