# Esta configuraçao utiliza o modulo do terraform-aws-modules/vpc/aws para criar uma VPC com sub-redes publicas e privadas, um NAT Gateway e um VPN Gateway.
# O código define a VPC e o CIDR, as zonas de disponibilidade (AZs), as sub-redes privadas e publicas, e habilita o NAT Gateway e o VPN Gateway.
# Além disso, o código adiciona tags para identificar a VPC como sendo gerenciada pelo Terraform e define o ambiente como "producao".

# Este arquivo define o provedor AWS e a versão do Terraform necessária para o projeto.
# O provedor AWS é utilizado para interagir com os recursos da Amazon Web Services.
# O código define a versão do provedor AWS como 5.96.0 e a região como us-east-1(N. Virginia)

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"

  name = var.aws_vpc_name
  cidr = var.aws_vpc_cidr

  azs             = var.aws_vpc_azs
  private_subnets = var.aws_vpc_private_subnets
  public_subnets  = var.aws_vpc_public_subnets

  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway

  single_nat_gateway = var.single_nat_gateway

  tags = merge(var.aws_project_tags, { "kubernetes.io/cluster/${var.aws_eks_cluster_name}" = "shared" })

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.aws_eks_cluster_name}" = "shared"
    "kubenetes.io/role/elb"                             = "1"

  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.aws_eks_cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"                   = "1"
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.36.0"

  cluster_name                             = var.aws_eks_cluster_name
  cluster_version                          = var.aws_eks_cluster_version
  enable_cluster_creator_admin_permissions = var.enable_cluster_creator_admin_permissions
  subnet_ids                               = module.vpc.private_subnets
  vpc_id                                   = module.vpc.vpc_id

  cluster_endpoint_public_access = var.cluster_endpoint_public_access

  eks_managed_node_groups = {
    default = {
      instance_types = var.aws_eks_mananaged_node_groups_instance_types
      desired_size   = var.desired_size
      max_size       = var.max_size
      min_size       = var.min_size
      disk_size      = var.disk_size

      tags = var.aws_project_tags
    }
  }
  tags = var.aws_project_tags
}

