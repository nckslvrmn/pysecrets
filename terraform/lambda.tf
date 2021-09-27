resource "aws_lambda_function" "secrets" {
  filename      = "${path.module}/placeholder.zip"
  function_name = "secrets"
  role          = aws_iam_role.secrets.arn
  handler       = "lambda.handler"
  runtime       = "python3.9"
  memory_size   = 2048
  timeout       = 5

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.secrets_files.id
      TTL_DAYS  = var.ttl_days
    }
  }

  lifecycle {
    ignore_changes = [filename]
  }
}

resource "aws_lambda_permission" "allow_apig" {
  statement_id  = "AllowExecutionFromAPIG"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secrets.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.secrets.execution_arn}/*/*/*"
}
