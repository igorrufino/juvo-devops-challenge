# Variables para o módulo de criação de infraestrutura na AWS com EKS
# Este arquivo contém as variáveis de configuração do Terraform para a infraestrutura AWS.}
variable "aws_region" {
  description = "AWS region é a região onde os recursos serão criados. Exemplo: us-east-1, us-west-2, etc"
  type        = string
}

variable "aws_vpc_name" {
  description = "Nome da VPC a ser criada na AWS"
  type        = string
}

variable "aws_vpc_cidr" {
  description = "CIDR da VPC a ser criada na AWS. Será utilizado para criar as sub-redes publicas e privadas"
  type        = string
}

variable "aws_vpc_azs" {
  description = "Zonas de disponibilidade (AZs) onde as sub-redes serão criadas. Exemplo: us-east-1a, us-east-1b, us-east-1c"
  type        = set(string)
}

variable "aws_vpc_private_subnets" {
  description = "CIDR das sub-redes privadas a serem criadas na VPC."
  type        = set(string)
}

variable "aws_vpc_public_subnets" {
  description = "CIDR das sub-redes publicas a serem criadas na VPC."
  type        = set(string)
}

variable "enable_nat_gateway" {
  description = "Habilita o NAT Gateway para as sub-redes publicas. O NAT Gateway é utilizado para permitir que as instancias nas sub-redes privadas acessem a internet."
  type        = bool
}

variable "enable_vpn_gateway" {
  description = "Habilita o VPN Gateway para a VPC. O VPN Gateway é utilizado para permitir a conexao entre a VPC e uma rede local."
  type        = bool
}

variable "single_nat_gateway" {
  description = "Habilita o NAT Gateway para as sub-redes publicas. O NAT Gateway é utilizado para permitir que as instancias nas sub-redes privadas acessem a internet."
  type        = bool
}


variable "aws_eks_cluster_name" {
  description = "Nome do cluster EKS a ser criado na AWS"
  type        = string
}

variable "aws_eks_cluster_version" {
  description = "Versão do cluster EKS a ser criado na AWS"
  type        = string
}

variable "enable_cluster_creator_admin_permissions" {
  description = "Habilita permissões administrativas para o criador do cluster EKS. Isso é útil para permitir que o criador do cluster tenha acesso total ao cluster."
  type        = bool
}

variable "cluster_endpoint_public_access" {
  description = "Habilita o acesso público ao endpoint do cluster EKS. Isso é útil para permitir que o cluster seja acessado de fora da VPC."
  type        = bool

}

variable "aws_eks_mananaged_node_groups_instance_types" {
  description = "Nome do tipo de instancia a ser utilizada nos grupos de nodos gerenciados do EKS. Exemplo: t3.xlarge, m5.large, etc"
  type        = set(string)
}

variable "desired_size" {
  description = "Tamanho desejado do grupo de nodos gerenciados do EKS. Exemplo: 2, 3, 4, etc"
  type        = number
}

variable "max_size" {
  description = "Tamanho máximo do grupo de nodos gerenciados do EKS. Exemplo: 2, 3, 4, etc"
  type        = number
  default     = 4
}

variable "min_size" {
  description = "Tamanho mínimo do grupo de nodos gerenciados do EKS. Exemplo: 2, 3, 4, etc"
  type        = number
  default     = 2
}

variable "disk_size" {
  description = "Tamanho do disco a ser utilizado nos grupos de nodos gerenciados do EKS. Exemplo: 20, 30, 40, etc"
  type        = number  
}

variable "aws_project_tags" {
  description = "Tags a serem aplicadas nos recursos criados na AWS. Exemplo: { Name = 'my-project', Environment = 'producao' }"
  type        = map(any)
}


