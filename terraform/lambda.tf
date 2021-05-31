resource "aws_lambda_function" "secrets" {
  filename      = "${path.module}/placeholder.zip"
  function_name = "secrets"
  role          = aws_iam_role.secrets.arn
  handler       = "lambda.handler"
  runtime       = "python3.8"
  memory_size   = 2048
  timeout       = 5

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.secrets_files.id
      TTL_DAYS  = var.ttl_days
    }
  }
}

resource "aws_lambda_permission" "allow_apig" {
  statement_id  = "AllowExecutionFromAPIG"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secrets.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.secret.execution_arn}/*/*/*"
}

resource "aws_lambda_function" "secrets_rewriter" {
  filename      = "${path.module}/placeholder.zip"
  function_name = "secrets_rewriter"
  role          = aws_iam_role.secrets_rewriter.arn
  handler       = "index.handler"
  runtime       = "nodejs12.x"
  memory_size   = 128
  timeout       = 1
  publish       = true
}
