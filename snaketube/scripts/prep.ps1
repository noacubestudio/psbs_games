param (
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath
)

$inFile = Join-Path $ProjectPath "nuworm.html"
$outFile = Join-Path $ProjectPath "index.html"
$mapFile = ".\scripts\replacements.txt"
$separator = "⦶"

$mapContent = Get-Content $mapFile -Raw

$parts = $mapContent -split [regex]::Escape($separator)
$parts = $parts | ForEach-Object { $_ -replace "`r", "" }
$parts = $parts[1..($parts.Count - 1)]
if ($parts.Count % 2 -ne 0) {
    throw "replacements.txt has an odd number of sections!"
}

$text = Get-Content $inFile -Raw
$totalReplacements = 0
for ($i = 0; $i -lt $parts.Count; $i += 2) {
    $search  = $parts[$i].TrimEnd()
    $replace = $parts[$i+1].TrimEnd()

    # Write-Host "Searched pattern (first 30 chars): $($search.Substring(0,[math]::Min(30,$search.Length)))"

    $pattern = [regex]::Escape($search)
    if ($text -match $pattern) {
        $text = $text -replace $pattern, $replace
        $totalReplacements++
    }
}

Set-Content $outFile -Value $text -NoNewline
Write-Host "Made $totalReplacements replacements and saved to $outFile"

if ($totalReplacements -eq 0) {
    throw "No replacements were made! Not pushing with butler."
}

butler push $outFile cubestudio/nuworm:web