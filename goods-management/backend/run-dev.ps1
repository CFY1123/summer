$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Compiling backend and building dependency classpath..."
& mvn.cmd -q compile dependency:build-classpath "-Dmdep.outputFile=target\classpath.txt"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$dependencyClasspath = Get-Content "target\classpath.txt" -Raw
$classpath = "target\classes;$dependencyClasspath"

Write-Host "Starting Spring Boot backend on http://localhost:8080/api"
& java -cp $classpath com.example.goods.GoodsManagementApplication

