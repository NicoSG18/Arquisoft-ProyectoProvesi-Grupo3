variable "ami_id" {}
variable "instance_type" {}
variable "key_name" {}
variable "subnet_id" {}
variable "sg_ssh_id" {}
variable "sg_http_id" {}
variable "sg_rabbit_id" {}

variable "rds_endpoint" {}
variable "rds_username" {}
variable "rds_password" {}

variable "rabbit_user" {}
variable "rabbit_password" {}

variable "email_host_user" {}
variable "email_host_password" {}

# Broker (RabbitMQ)
resource "aws_instance" "broker" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  key_name                    = var.key_name
  vpc_security_group_ids      = [var.sg_ssh_id, var.sg_rabbit_id]

  user_data = templatefile("${path.module}/../../templates/user_data_broker.sh.tftpl", {
    rabbit_user     = var.rabbit_user
    rabbit_password = var.rabbit_password
  })

  tags = { Name = "broker-instance" }
}

# Producer
resource "aws_instance" "producer" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  key_name               = var.key_name
  vpc_security_group_ids = [var.sg_ssh_id]

  user_data = templatefile("${path.module}/../../templates/user_data_producer.sh.tftpl", {
    broker_private_ip = aws_instance.broker.private_ip
    rabbit_user       = var.rabbit_user
    rabbit_password   = var.rabbit_password
  })

  tags = { Name = "producer-instance" }
}

# Subscriber (Django app + subscriber.py)
resource "aws_instance" "subscriber" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  key_name               = var.key_name
  vpc_security_group_ids = [var.sg_ssh_id, var.sg_http_id]

  user_data = templatefile("${path.module}/../../templates/user_data_subscriber.sh.tftpl", {
    broker_private_ip   = aws_instance.broker.private_ip
    rds_endpoint        = var.rds_endpoint
    rds_username        = var.rds_username
    rds_password        = var.rds_password
    email_host_user     = var.email_host_user
    email_host_password = var.email_host_password
  })

  tags = { Name = "subscriber-instance" }
}

output "broker_public_ip"     { value = aws_instance.broker.public_ip }
output "producer_public_ip"   { value = aws_instance.producer.public_ip }
output "subscriber_public_ip" { value = aws_instance.subscriber.public_ip }
