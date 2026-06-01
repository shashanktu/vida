from vida.utils import script_validator

invalid_hcl = """
    provider "azurerm" {
  features 
}

resource "azurerm_resource_group" "example" {
  name = "example-resources"
  location = "East US"
  # Missing closing brace below
  

output "resource_group_name" {
  value = azurerm_resource_group.example.name
}
    """
print(script_validator.validate_hcl(invalid_hcl))
