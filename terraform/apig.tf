resource "aws_apigatewayv2_api" "secret" {
  name          = "secrets"
  protocol_type = "HTTP"

}

resource "aws_apigatewayv2_domain_name" "secret" {
  domain_name = "secret.slvr.io"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.example.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "domain" {
  api_id      = aws_apigatewayv2_api.secrets.id
  domain_name = aws_apigatewayv2_domain_name.secret.id
  stage       = "$default"
}

resource "aws_apigatewayv2_route" "encrypt" {
  api_id    = aws_apigatewayv2_api.secrets.id
  route_key = "/encrypt"
}

resource "aws_apigatewayv2_integration" "encrypt" {
  api_id           = aws_apigatewayv2_api.secrets.id
  integration_type = "AWS"

  connection_type        = "INTERNET"
  description            = "encrypt"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.secrets.invoke_arn
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "decrypt" {
  api_id    = aws_apigatewayv2_api.secrets.id
  route_key = "/decrypt"
}

resource "aws_apigatewayv2_integration" "decrypt" {
  api_id           = aws_apigatewayv2_api.secrets.id
  integration_type = "AWS"

  connection_type        = "INTERNET"
  description            = "decrypt"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.secrets.invoke_arn
  payload_format_version = "1.0"
}
