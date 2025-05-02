# =========================================
# Variáveis
# =========================================
# Este arquivo contém todas as variáveis usadas nos módulos

variable "bucket_name" {
  description = "Nome do bucket S3 para armazenar o estado do Terraform"
  type        = string
  nullable    = false
}

variable "force_destroy" {
  description = "Permite que o Terraform destrua o bucket mesmo se contiver objetos"
  type        = bool
  nullable    = false
}

variable "object_ownership" {
  description = "Controle de propriedade de objetos no bucket"
  type        = string
  nullable    = false
}

variable "block_public_acls" {
  description = "Bloqueia ACLs públicas"
  type        = bool
  nullable    = false
}

variable "block_public_policy" {
  description = "Bloqueia políticas públicas"
  type        = bool
  nullable    = false
}

variable "ignore_public_acls" {
  description = "Ignora ACLs públicas existentes"
  type        = bool
  nullable    = false
}

variable "restrict_public_buckets" {
  description = "Restringe acesso público ao bucket"
  type        = bool
  nullable    = false
}



variable "versioning" {
  description = "Habilita versionamento de objetos no bucket"
  type        = map(string)
  nullable    = false
}

variable "aws_project_tags" {
  description = "Tags a serem aplicadas nos recursos criados na AWS. Exemplo: { Name = 'my-project', Environment = 'producao' }"
  type        = map(any)
  nullable    = false
}