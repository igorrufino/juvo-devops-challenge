
# =========================================
# Criação do Bucket S3 e Tabela DynamoDB
# =========================================
# Este é o módulo criado para criar o bucket S3 e a tabela DynamoDB para armazenar o estado do Terraform e controlar Locks
# Tabela DynamoDB é criado para não permitir que vários usuários possam mofificar a infra ao mesmo tempo, para desenvolvimento não é tão relevante, mas para produção é importante.
module "s3_bucket" {
  source                  = "terraform-aws-modules/s3-bucket/aws"
  version                 = "4.8.0"
  bucket                  = var.bucket_name
  force_destroy           = var.force_destroy
  object_ownership        = var.object_ownership
  block_public_acls       = var.block_public_acls       # Bloqueia ACLs públicas
  block_public_policy     = var.block_public_policy     # Bloqueia políticas públicas
  ignore_public_acls      = var.ignore_public_acls      # Ignora ACLs públicas existentes
  restrict_public_buckets = var.restrict_public_buckets # Restringe acesso público ao bucket
  versioning              = var.versioning
  tags                    = var.aws_project_tags
}