resource "aws_route53_record" "secret" {
  name    = aws_apigatewayv2_domain_name.secret.domain_name
  type    = "A"
  zone_id = aws_route53_zone.example.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.secret.domain_name_configuration.0.target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.secret.domain_name_configuration.0.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "secrets" {
  name    = "secrets.slvr.io"
  type    = "A"
  zone_id = aws_route53_zone.example.zone_id

  alias {
    name                   = aws_cloudfront_distribution.secrets.domain_name
    zone_id                = aws_cloudfront_distribution.secrets.hosted_zone_id
    evaluate_target_health = false
  }
}
