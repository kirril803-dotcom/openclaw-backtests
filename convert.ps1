$json = Get-Content "$env:USERPROFILE\.openclaw\workspace\openclaw-backtests\data\btc_raw.json" -Raw | ConvertFrom-Json
$lines = @('datetime,open,high,low,close,volume')
foreach($k in $json) {
    $ts = [math]::Floor($k[0] / 1000)
    $lines += "$ts,$($k[1]),$($k[2]),$($k[3]),$k[4],$($k[5])"
}
$lines | Out-File -FilePath "$env:USERPROFILE\.openclaw\workspace\openclaw-backtests\data\btc_data.csv" -Encoding UTF8
Write-Host 'Done!'
