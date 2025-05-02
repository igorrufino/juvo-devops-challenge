# Criar uma role IAM para o EBS CSI Driver com permissões para usar o KMS.
# Essa role será utilizada pelo driver EBS CSI para gerenciar volumes EBS,
# incluindo operações de criptografia e descriptografia usando chaves KMS.

module "ebs_csi_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.39.0"

  role_name             = "AmazonEKS_EBS_CSI_DriverRole-${module.eks.cluster_name}"
  attach_ebs_csi_policy = true

  oidc_providers = {
    eks = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }
  
  depends_on = [module.eks]
}