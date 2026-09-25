aws_region   = "eu-central-1"
environment  = "dev"
cluster_name = "task-manager-eks"

vpc_cidr = "10.0.0.0/16"

node_instance_type = "t3.medium"

node_min_size     = 1
node_desired_size = 2
node_max_size     = 3