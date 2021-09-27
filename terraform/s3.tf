resource "aws_s3_bucket" "secrets_files" {
  bucket = "${var.prefix}-secrets-file-store"
  acl    = "private"

  lifecycle_rule {
    id      = "clean"
    enabled = true

    expiration {
      days = tonumber(var.ttl_days) + 1
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block_all" {
  bucket = aws_s3_bucket.secrets_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "secrets_site" {
  bucket = var.domain_name
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "site_block_all" {
  bucket = aws_s3_bucket.secrets_site.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
