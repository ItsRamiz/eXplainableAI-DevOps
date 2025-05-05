# Initializing S3 Bucket and Uploading Files

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "explainingai"
  acl    = "private"
}

locals {
  static_files = fileset("static", "**")
}

resource "aws_s3_bucket_object" "static_files" {
  for_each = { for file in local.static_files : file => file }

  bucket = aws_s3_bucket.my_bucket.bucket
  key    = each.key
  source = "static/${each.key}"
  acl    = "private"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "app_sg" {
  name        = "app-sg"
  description = "Allow HTTP ports for app containers"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5000
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_iam_role" "ec2_instance_role" {
  name = "ec2-ecr-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_access" {
  role       = aws_iam_role.ec2_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_instance_role.name
}

resource "aws_key_pair" "existing_key" {
  key_name   = "key-075bac73baede8283"
  public_key = file("~/.ssh/id_rsa.pub")
}

# EC2 Backend
resource "aws_instance" "backend" {
  ami                    = "ami-0c2b8ca1dad447f8a"  # Ubunutu
  instance_type          = "t2.micro"
  subnet_id              = data.aws_subnets.default.ids[0]
  security_groups        = [aws_security_group.app_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  key_name               = aws_key_pair.existing_key.key_name

  tags = {
    Name = "backend"
  }
}

# EC2 Frontend
resource "aws_instance" "frontend" {
  ami                    = "ami-0c2b8ca1dad447f8a" # Ubuntu
  instance_type          = "t2.micro"
  subnet_id              = data.aws_subnets.default.ids[1]
  security_groups        = [aws_security_group.app_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  key_name               = aws_key_pair.existing_key.key_name

  tags = {
    Name = "frontend"
  }
}

output "frontend_public_ip" {
  value = aws_instance.frontend.public_ip
}

output "backend_private_ip" {
  value = aws_instance.backend.private_ip
}
