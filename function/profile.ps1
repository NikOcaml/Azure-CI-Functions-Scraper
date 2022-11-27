if ($env:MSI_SECRET) {
    Disable-AzContextAutosave -Scope Process | Out-Null
    Connect-AzAccount -Identity
}
$env:AZURE_STORAGE_CONNECTION_STRING="Your Connection String"
