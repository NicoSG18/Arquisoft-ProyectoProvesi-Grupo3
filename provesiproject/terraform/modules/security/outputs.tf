output "sg_trafico_ssh_id"    { value = aws_security_group.trafico_ssh.id }
output "sg_trafico_db_id"     { value = aws_security_group.trafico_db.id }
output "sg_trafico_http_id"   { value = aws_security_group.trafico_http.id }
output "sg_trafico_rabbit_id" { value = aws_security_group.trafico_rabbit.id }
