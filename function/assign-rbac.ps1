#Enables System-managed identity and then assigns role-based access control (contributor role)
#Change nameofyourfunctionapp and nameofyourresourcegroup to your values
Update-AzFunctionApp -Name nameofyourfunctionapp `
    -ResourceGroupName nameofyourresourcegroup `
    -IdentityType SystemAssigned
$SP=(Get-AzADServicePrincipal -DisplayName nameofyourfunctionapp).Id
$RG=(Get-AzResourceGroup -Name nameofyourresourcegroup).ResourceId
New-AzRoleAssignment -ObjectId $SP -RoleDefinitionName "Contributor" -Scope $RG