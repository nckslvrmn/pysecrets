resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "SecretsS3Origin"
}

resource "aws_cloudfront_distribution" "secrets" {
  origin {
    domain_name = aws_s3_bucket.secrets_site.bucket_regional_domain_name
    origin_id   = aws_cloudfront_origin_access_identity.oai.id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Secrets Site"
  default_root_object = "index.html"

  aliases = [var.main_domain_name]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = aws_cloudfront_origin_access_identity.oai.id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  ordered_cache_behavior {
    path_pattern     = "/secret/*"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = aws_cloudfront_origin_access_identity.oai.id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000

    lambda_function_association {
      event_type   = "origin-request"
      lambda_arn   = aws_lambda_function.secrets_rewriter.qualified_arn
      include_body = false
    }
  }

  price_class = "PriceClass_100"

  viewer_certificate {
    minimum_protocol_version = "TLSv1.2_2018"
    ssl_support_method       = "sni-only"
    acm_certificate_arn      = var.acm_arn
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}
