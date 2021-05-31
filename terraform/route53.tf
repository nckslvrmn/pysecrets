resource "aws_route53_record" "secret" {
  name    = var.api_domain_name
  type    = "A"
  zone_id = var.hosted_zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.secret.domain_name_configuration.0.target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.secret.domain_name_configuration.0.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "secrets" {
  name    = var.main_domain_name
  type    = "A"
  zone_id = var.hosted_zone_id

  alias {
    name                   = aws_cloudfront_distribution.secrets.domain_name
    zone_id                = aws_cloudfront_distribution.secrets.hosted_zone_id
    evaluate_target_health = false
  }
}
