# 'Az.ContainerInstance'='3.1.0' is needed inside the app file requirements.psd1 
param($Timer)

$volume = New-AzContainerGroupVolumeObject -Name "Name of the mounted volume object" -AzureFileShareName "The Azure Fileshare name" -AzureFileStorageAccountName "Storage Account Name" -AzureFileStorageAccountKey (ConvertTo-SecureString "Storage Account Key" -AsPlainText -Force)
$mount = New-AzContainerInstanceVolumeMountObject -MountPath "/SeleniumApp" -Name "The Azure Fileshare name"
$container = New-AzContainerInstanceObject -Name "Name of the container instance" -Image eth11/sel-chrome-local:v01 -VolumeMount $mount
New-AzContainerGroup -ResourceGroupName scraper -Name "Name of the container group" -Location germanywestcentral -Container $container -RestartPolicy "Never" -Volume $volume

#Since the cronjob doesn't trigger on the weekend, the first scraping of the week takes a bit longer
$Calendar = Get-Date
If ($Calendar.DayOfWeek.value__ -eq '1' -And $Calendar.Hour -lt '9') {
Start-Sleep -Seconds 55
}
Else {
Start-Sleep -Seconds 30
}

Remove-AzContainerGroup -Name freelance-scraper-cg -ResourceGroupName scraper