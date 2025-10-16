variable "vpc_id" { type = string }
variable "ssh_allowed_cidr" { type = string }

# trafico-ssh (22)
resource "aws_security_group" "trafico_ssh" {
  name        = "trafico-ssh"
  description = "Permite SSH"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr] # el lab usa Anywhere-IPv4, puedes restringir aquí. :contentReference[oaicite:9]{index=9}
  }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] } # mantener reglas de salida por defecto. :contentReference[oaicite:10]{index=10}
  tags = { Name = "trafico-ssh" }
}

# trafico-db (5432)
resource "aws_security_group" "trafico_db" {
  name        = "trafico-db"
  description = "Permite PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # lab: Anywhere-IPv4 (para demo). :contentReference[oaicite:11]{index=11}
  }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "trafico-db" }
}

# trafico-http (8080)
resource "aws_security_group" "trafico_http" {
  name        = "trafico-http"
  description = "Permite HTTP app 8080"
  vpc_id      = var.vpc_id

  ingress {
    description = "App 8080"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # lab: Anywhere-IPv4. :contentReference[oaicite:12]{index=12}
  }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "trafico-http" }
}

# trafico-rabbit (15672, 5672)
resource "aws_security_group" "trafico_rabbit" {
  name        = "trafico-rabbit"
  description = "Permite RabbitMQ y dashboard"
  vpc_id      = var.vpc_id

  ingress {
    description = "Rabbit dashboard"
    from_port   = 15672
    to_port     = 15672
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # lab dashboard. :contentReference[oaicite:13]{index=13}
  }

  ingress {
    description = "Rabbit AMQP"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # lab AMQP. :contentReference[oaicite:14]{index=14}
  }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "trafico-rabbit" }
}
