param($Timer)
#Change all the strings to your values
$volume = New-AzContainerGroupVolumeObject -Name "Name of the mounted volume object" -AzureFileShareName "The Azure Fileshare name" -AzureFileStorageAccountName "Storage Account Name" -AzureFileStorageAccountKey (ConvertTo-SecureString "Storage Account Key" -AsPlainText -Force)
$mount = New-AzContainerInstanceVolumeMountObject -MountPath "/SeleniumApp" -Name "The Azure Fileshare name"
$container = New-AzContainerInstanceObject -Name "Name of the container instance" -Image eth11/sel-chrome-local:v01 -VolumeMount $mount
New-AzContainerGroup -ResourceGroupName "Name of the resource group" -Name "Name of the container group" -Location germanywestcentral -Container $container -RestartPolicy "Never" -Volume $volume

# Wait for the updated watermark for a maximum of 5*15 seconds
$iterator=1
while ((Get-AzStorageFile -ShareName "The Azure Fileshare name" -path "data/watermark.json").LastModified -lt $now -And $iterator -lt 6) {
    $iterator++
    Start-Sleep -Seconds 15
}

Remove-AzContainerGroup -Name "Name of the container group" -ResourceGroupName "Name of the resource group"