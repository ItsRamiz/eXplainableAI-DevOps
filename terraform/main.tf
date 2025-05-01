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
