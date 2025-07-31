variable "aws_region" {
  description = "AWS Deployment Region"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name for static files"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
}

variable "key_name" {
  description = "Name of existing key pair"
  type        = string
}

variable "public_key_path" {
  description = "Path to public SSH key"
  type        = string
}
