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
  backend "s3" {
    region = "us-east-1"
    # Configurações fornecidas via linha de comando
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}


provider "aws" {
  region = var.aws_region
}