Write-Host -NoNewline "Checking for mpremote..."
try {
    $command = Get-Command mpremote -ErrorAction Stop
    Write-Output "mpremote is available."
} catch {
    Write-Output "mpremote is not found."
    Write-Host "Please install mpremote by running 'pip install mpremote'"
    exit 1
}

$DEVICES = mpremote connect list
if ($DEVICES -eq $null) {
  Write-Host "No MicroPython devices found"
  exit 1
} elseif ( {$DEVICES | Select-String -Pattern "MicroPython" } -ne $null) {
  Write-Host -NoNewline "Devices found, incorrectly named, trying first one "
  $DEVICES = $DEVICES | ForEach-Object { $_ -split " " | Select-Object -First 1 }
  Write-Host "($DEVICES)"
} else {
  Write-Host -NoNewline "MicroPython Devices found, using first one "
  $DEVICES = $DEVICES | Select-String -Pattern "MicroPython" | ForEach-Object { $_ -split " " | Select-Object -First 1 }
  Write-Host "($DEVICES)"
}

if ($DEVICES -eq $null) {
  Write-Host "No MicroPython devices found in FS mode"
  exit 1
}

$DEVICE =  ($DEVICES.Count -ne 1) ? $DEVICES[0] : $DEVICES

Write-Host "Copying Enviro firmware files to $DEVICE"

function create_directory {
  param($dir)
  Write-Host -NoNewline "> creating directory $dir"

  $RESULT = mpremote connect $DEVICE mkdir $dir
  $ERROR = $LASTEXITCODE

  if ($ERROR -eq 0) {
    Write-Host " .. done!"
  }
  else {
    if ($RESULT -match "EEXIST") {
      Write-Host " .. already exists, skipping."
    }
    else {
      Write-Host " .. failed!"
      Write-Host "! it looks like this device is already in use - is Thonny running?"
      exit 1
    }
  }
}

function mp_copy {
  param($source, $destination)
  foreach ($file in (Get-ChildItem -Path $source)) {
    Write-Host -NoNewline "> copying file $($file.FullName) to $destination"
    mpremote connect $DEVICE cp $file.FullName $destination > $null
    if ($LASTEXITCODE -eq 0) {
      Write-Host " .. done!"
    }
    else {
      Write-Host " .. failed!"
    }
  }
}

create_directory "enviro"
create_directory "enviro/boards"
create_directory "enviro/destinations"
create_directory "enviro/html"
create_directory "enviro/html/images"
create_directory "phew"
create_directory "phew/phew"

mp_copy "main.py" ":"

mp_copy "enviro/*.py" ":enviro/"

mp_copy "enviro/boards/*.py" ":enviro/boards/"
mp_copy "enviro/destinations/*.py" ":enviro/destinations/"

mp_copy "enviro/html/*.html" ":enviro/html/"

mp_copy "enviro/html/images/*" ":enviro/html/images/"

mp_copy "phew/__init__.py" ":phew/"
mp_copy "phew/phew/*.py" ":phew/phew/"
