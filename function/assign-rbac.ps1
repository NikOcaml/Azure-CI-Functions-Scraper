#Enables System-managed identity and then assigns role-based access control (contributor role).
Update-AzFunctionApp -Name myfunctionapp `
    -ResourceGroupName myfunctionapp `
    -IdentityType SystemAssigned
$SP=(Get-AzADServicePrincipal -DisplayName orch-scraper).Id
$RG=(Get-AzResourceGroup -Name scraper).ResourceId
New-AzRoleAssignment -ObjectId $SP -RoleDefinitionName "Contributor" -Scope $RG