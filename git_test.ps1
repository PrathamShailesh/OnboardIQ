cd d:\vscode\OnboardIQ
Write-Output "Testing git..." | Out-File -FilePath git_test_output.txt
$env:GIT_REDIRECT_STDERR = "2>&1"
git status 2>&1 | Out-File -FilePath git_test_output.txt -Append
Write-Output "Done" | Out-File -FilePath git_test_output.txt -Append
Get-Content git_test_output.txt
