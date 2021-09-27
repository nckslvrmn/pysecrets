locals {
  static_routes = {
    "site.css" : {
      "path" : "site.css",
      "type" : "text/css"
    },
    "main.js" : {
      "path" : "main.js",
      "type" : "text/javascript"
    },
    "files" : {
      "path" : "files.html",
      "type" : "text/html"
    }
  }
  lambda_routes = [
    "encrypt",
    "decrypt"
  ]
}

# Root Route
resource "aws_api_gateway_method" "root" {
  rest_api_id   = aws_api_gateway_rest_api.secrets.id
  resource_id   = aws_api_gateway_rest_api.secrets.root_resource_id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "root" {
  rest_api_id             = aws_api_gateway_rest_api.secrets.id
  resource_id             = aws_api_gateway_rest_api.secrets.root_resource_id
  http_method             = aws_api_gateway_method.root.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  credentials             = aws_iam_role.apigateway.arn
  uri                     = "arn:aws:apigateway:us-east-1:s3:path/${var.domain_name}/index.html"
}

resource "aws_api_gateway_method_response" "root_response_200" {
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_rest_api.secrets.root_resource_id
  http_method = aws_api_gateway_method.root.http_method
  status_code = "200"

  response_models = {
    "text/html" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "root_response" {
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_rest_api.secrets.root_resource_id
  http_method = aws_api_gateway_method.root.http_method
  status_code = aws_api_gateway_method_response.root_response_200.status_code
}


# Static Routes
resource "aws_api_gateway_resource" "static" {
  for_each    = local.static_routes
  path_part   = each.key
  parent_id   = aws_api_gateway_rest_api.secrets.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.secrets.id
}

resource "aws_api_gateway_method" "static" {
  for_each      = local.static_routes
  rest_api_id   = aws_api_gateway_rest_api.secrets.id
  resource_id   = aws_api_gateway_resource.static[each.key].id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "static" {
  for_each                = local.static_routes
  rest_api_id             = aws_api_gateway_rest_api.secrets.id
  resource_id             = aws_api_gateway_resource.static[each.key].id
  http_method             = aws_api_gateway_method.static[each.key].http_method
  integration_http_method = "GET"
  type                    = "AWS"
  credentials             = aws_iam_role.apigateway.arn
  uri                     = "arn:aws:apigateway:us-east-1:s3:path/${var.domain_name}/${each.value["path"]}"
}

resource "aws_api_gateway_method_response" "static_response_200" {
  for_each    = local.static_routes
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_resource.static[each.key].id
  http_method = aws_api_gateway_method.static[each.key].http_method
  status_code = "200"

  response_models = {
    "${each.value["type"]}" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "static_response" {
  for_each    = local.static_routes
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_resource.static[each.key].id
  http_method = aws_api_gateway_method.static[each.key].http_method
  status_code = aws_api_gateway_method_response.static_response_200[each.key].status_code
}


### secret_id Route
resource "aws_api_gateway_resource" "secret" {
  path_part   = "secret"
  parent_id   = aws_api_gateway_rest_api.secrets.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.secrets.id
}

resource "aws_api_gateway_resource" "secret_id" {
  path_part   = "{secret_id}"
  parent_id   = aws_api_gateway_resource.secret.id
  rest_api_id = aws_api_gateway_rest_api.secrets.id
}

resource "aws_api_gateway_method" "secret_id" {
  rest_api_id   = aws_api_gateway_rest_api.secrets.id
  resource_id   = aws_api_gateway_resource.secret_id.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "secret_id" {
  rest_api_id             = aws_api_gateway_rest_api.secrets.id
  resource_id             = aws_api_gateway_resource.secret_id.id
  http_method             = aws_api_gateway_method.secret_id.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  credentials             = aws_iam_role.apigateway.arn
  uri                     = "arn:aws:apigateway:us-east-1:s3:path/${var.domain_name}/secret.html"
}

resource "aws_api_gateway_method_response" "secret_id_response_200" {
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_resource.secret_id.id
  http_method = aws_api_gateway_method.secret_id.http_method
  status_code = "200"

  response_models = {
    "text/html" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "secret_id_response" {
  rest_api_id = aws_api_gateway_rest_api.secrets.id
  resource_id = aws_api_gateway_resource.secret_id.id
  http_method = aws_api_gateway_method.secret_id.http_method
  status_code = aws_api_gateway_method_response.secret_id_response_200.status_code
}


### Lambda Routes
resource "aws_api_gateway_resource" "lambda" {
  for_each    = toset(local.lambda_routes)
  path_part   = each.value
  parent_id   = aws_api_gateway_rest_api.secrets.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.secrets.id
}

resource "aws_api_gateway_method" "lambda" {
  for_each      = toset(local.lambda_routes)
  rest_api_id   = aws_api_gateway_rest_api.secrets.id
  resource_id   = aws_api_gateway_resource.lambda[each.value].id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  for_each                = toset(local.lambda_routes)
  rest_api_id             = aws_api_gateway_rest_api.secrets.id
  resource_id             = aws_api_gateway_resource.lambda[each.value].id
  http_method             = aws_api_gateway_method.lambda[each.value].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.secrets.invoke_arn
}
