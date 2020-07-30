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
  bucket = var.main_domain_name
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "site_block_all" {
  bucket = aws_s3_bucket.secrets_site.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.secrets_site.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.oai.iam_arn]
    }
  }

  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.secrets_site.arn]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.oai.iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "oai" {
  bucket = aws_s3_bucket.secrets_site.id
  policy = data.aws_iam_policy_document.s3_policy.json
}
