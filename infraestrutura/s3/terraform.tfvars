bucket_name             = "score-plataform-terraform"
force_destroy           = true
object_ownership        = "ObjectWriter"
block_public_acls       = true
block_public_policy     = true
ignore_public_acls      = true
restrict_public_buckets = true
versioning = {
  enabled = false #para habilitar baackups de arquivos utilize a opção como true ou false
}
aws_project_tags = {
  Terraform   = "true"
  Environment = "producao"
  project     = "score-plataform"
  owner       = "igor.rufino"
}