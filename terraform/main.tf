provider "aws" {
  region = "us-east-1"
}

data "aws_key_pair" "existing" {
  key_name = "terraform_aws_key"
  filter {
    name   = "key-name"
    values = ["terraform_aws_key"]
  }
}

resource "aws_key_pair" "deployer" {
  count = length(data.aws_key_pair.existing.key_name) == 0 ? 1 : 0
  key_name   = "terraform_aws_key"
  public_key = file("~/.ssh/id_ed25519.pub")
}

resource "aws_instance" "minikube" {
  ami               = "ami-04ffc9f7871904759" # Ubuntu Server 22.04 LTS (HVM)
  instance_type     = "t3.large"
  availability_zone = "us-east-1b"
  key_name          = coalesce(data.aws_key_pair.existing.key_name, "terraform_aws_key")

  root_block_device {
    volume_size = 50 # Size in GB
    volume_type = "gp2" # General Purpose SSD
  }

  tags = {
    Name = "minikube-server"
  }
}

resource "aws_eip" "elastic_ip" {
  instance = aws_instance.minikube.id
  vpc      = true
}

resource "aws_route53_record" "fqdn" {
  zone_id = "Z3RUW5P7TDNES4"
  name    = "malamig-na-serbisyo.climacs.net"
  type    = "A"
  ttl     = "300"
  records = [aws_eip.elastic_ip.public_ip]
}

output "instance_ip" {
  value = aws_eip.elastic_ip.public_ip
}
