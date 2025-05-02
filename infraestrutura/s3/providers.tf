# Este arquivo contém a configuração do provider AWS para o Terraform.
# O provider AWS é utilizado para interagir com os recursos da Amazon Web Services.
# O código define a versão do provider AWS como 5.96.0 e a região está definida em terraform.tfvars.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.96.0"
    }
  }
}