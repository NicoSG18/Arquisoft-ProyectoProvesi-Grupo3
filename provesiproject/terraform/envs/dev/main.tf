terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# --- NETWORK ---
module "network" {
  source             = "../../modules/network"
  vpc_cidr_block     = var.vpc_cidr_block
  public_subnet_cidr = var.public_subnet_cidr
}

# --- SECURITY GROUPS ---
module "security" {
  source           = "../../modules/security"
  vpc_id           = module.network.vpc_id
  ssh_allowed_cidr = var.ssh_allowed_cidr
}

# --- RDS POSTGRES ---
module "rds" {
  source                = "../../modules/rds"
  db_name               = "monitoring_db"
  db_username           = var.db_username       # por defecto "monitoring_user"
  db_password           = var.db_password       # por defecto "isis2503"
  publicly_accessible   = true                  # el enunciado opera con endpoint público y SG de DB. :contentReference[oaicite:3]{index=3}
  vpc_security_group_ids = [ module.security.sg_trafico_db_id ]
  subnet_ids            = [ module.network.public_subnet_id ] # simple (1 AZ) para el lab
}

# --- AMIs Ubuntu 24.04 LTS ---
data "aws_ami" "ubuntu_2404" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# --- COMPUTE (EC2s) ---
module "compute" {
  source               = "../../modules/compute"
  ami_id               = data.aws_ami.ubuntu_2404.id
  instance_type        = "t2.nano"     # como pide el lab. :contentReference[oaicite:4]{index=4}
  key_name             = var.key_name
  subnet_id            = module.network.public_subnet_id

  # Security Groups
  sg_ssh_id            = module.security.sg_trafico_ssh_id
  sg_http_id           = module.security.sg_trafico_http_id
  sg_rabbit_id         = module.security.sg_trafico_rabbit_id

  # RDS endpoint (para subscriber settings.py)
  rds_endpoint         = module.rds.db_endpoint
  rds_username         = var.db_username
  rds_password         = var.db_password

  # Credenciales RabbitMQ (lab)
  rabbit_user          = "monitoring_user"
  rabbit_password      = "isis2503"

  # Email (Gmail App Password, lab 3.4)
  email_host_user      = var.email_host_user     # tu cuenta gmail
  email_host_password  = var.email_host_password # app password de Gmail (2FA) :contentReference[oaicite:5]{index=5}
}
