$commands = $(Get-ChildItem ./_CI/scripts -Exclude "_*" |select Name |% {$_.name.split('.')[0]})

function New-Alias{
    param (
        $command
    )
    $Path="_CI/scripts/$command.py"
    $CommandText = 'function _'+$command+'() { if (Test-Path '+$path+') {python '+$path+' $args} else{write-host "executable not found at"'+$path+' -ForegroundColor Red} }'

    Write-Output $CommandText
}

foreach ($command in $commands) {
    Invoke-Expression(New-Alias($command))
}
