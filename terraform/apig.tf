resource "aws_apigatewayv2_api" "secret" {
  name          = "secrets"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://${var.main_domain_name}"]
    allow_methods = ["POST"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.secret.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_domain_name" "secret" {
  domain_name = var.api_domain_name

  domain_name_configuration {
    certificate_arn = var.acm_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "domain" {
  api_id      = aws_apigatewayv2_api.secret.id
  domain_name = aws_apigatewayv2_domain_name.secret.id
  stage       = aws_apigatewayv2_stage.default.id
}

resource "aws_apigatewayv2_route" "encrypt" {
  api_id    = aws_apigatewayv2_api.secret.id
  route_key = "POST /encrypt"
  target    = "integrations/${aws_apigatewayv2_integration.encrypt.id}"
}

resource "aws_apigatewayv2_integration" "encrypt" {
  api_id           = aws_apigatewayv2_api.secret.id
  integration_type = "AWS_PROXY"

  description            = "encrypt"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.secrets.invoke_arn
  payload_format_version = "1.0"

  lifecycle {
    ignore_changes = [passthrough_behavior]
  }
}

resource "aws_apigatewayv2_route" "decrypt" {
  api_id    = aws_apigatewayv2_api.secret.id
  route_key = "POST /decrypt"
  target    = "integrations/${aws_apigatewayv2_integration.decrypt.id}"
}

resource "aws_apigatewayv2_integration" "decrypt" {
  api_id           = aws_apigatewayv2_api.secret.id
  integration_type = "AWS_PROXY"

  description            = "decrypt"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.secrets.invoke_arn
  payload_format_version = "1.0"

  lifecycle {
    ignore_changes = [passthrough_behavior]
  }
}
