variable "db_name"  { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }
variable "publicly_accessible" { type = bool }
variable "vpc_security_group_ids" { type = list(string) }
variable "subnet_ids" { type = list(string) }

# Para el lab usamos 1 subnet pública (simple). En productivo: subnet group con >=2 AZ.
resource "aws_db_subnet_group" "this" {
  name       = "lab6-rds-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "postgres" {
  identifier              = "monitoring-db"          # lab. :contentReference[oaicite:15]{index=15}
  allocated_storage       = 20
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = "db.t3.micro"
  username                = var.db_username
  password                = var.db_password
  db_name                 = var.db_name
  publicly_accessible     = var.publicly_accessible
  vpc_security_group_ids  = var.vpc_security_group_ids
  db_subnet_group_name    = aws_db_subnet_group.this.name
  skip_final_snapshot     = true

  backup_retention_period = 0
  deletion_protection     = false

  tags = { Name = "monitoring-db" }
}

output "db_endpoint" {
  value = aws_db_instance.postgres.address
}
