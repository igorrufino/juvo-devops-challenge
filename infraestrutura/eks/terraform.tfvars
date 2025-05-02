# Variables de configuração do Terraform para a infraestrutura AWS
# Este arquivo contém as variáveis de configuração do Terraform para a infraestrutura AWS.
aws_region                                   = "us-east-1"
aws_vpc_name                                 = "vpc-score-plataform"
aws_vpc_cidr                                 = "10.0.0.0/16"
aws_vpc_azs                                  = ["us-east-1a", "us-east-1b", "us-east-1c"]
aws_vpc_private_subnets                      = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
aws_vpc_public_subnets                       = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
enable_nat_gateway                           = true
enable_vpn_gateway                           = true
single_nat_gateway                           = true
aws_eks_cluster_name                         = "cluster-terraform"
aws_eks_cluster_version                      = "1.32"
enable_cluster_creator_admin_permissions     = true
cluster_endpoint_public_access               = true
aws_eks_mananaged_node_groups_instance_types = ["t3.medium"]
desired_size                                 = 4
max_size                                     = 4
min_size                                     = 2
disk_size                                    = 20
aws_project_tags = {
  Terraform   = "true"
  Environment = "producao"
  project     = "score-plataform"
  owner       = "igor.rufino"
}
