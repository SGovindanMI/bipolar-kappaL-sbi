param([Parameter(Mandatory=$true)][string]$DocumentPath)
$ErrorActionPreference = 'Stop'
$taskDocPath = (Resolve-Path -LiteralPath $DocumentPath).Path
$taskRepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $taskDocPath.StartsWith($taskRepoPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The export source must be inside this research working copy.'
}
$taskPdfPath = [IO.Path]::ChangeExtension($taskDocPath, '.pdf')
$taskWord = $null
$taskDoc = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskDoc = $taskWord.Documents.Open($taskDocPath, $false, $true)
    $taskDoc.ExportAsFixedFormat($taskPdfPath, 17)
} finally {
    if ($null -ne $taskDoc) { $taskDoc.Close(0) }
    if ($null -ne $taskWord) { $taskWord.Quit() }
}
Get-Item -LiteralPath $taskPdfPath | Select-Object FullName,Length
