resource "aws_lambda_function" "secrets" {
  filename      = "placeholder.zip"
  function_name = "secrets"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda.handler"
  runtime       = "python3.8"
  memory_size   = 2048
  timeout       = 5

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.secrets_files.name
      TTL_DAYS  = var.ttl_days
    }
  }
}

resource "aws_lambda_function" "secrets_rewriter" {
  filename      = "placeholder.zip"
  function_name = "secrets_rewriter"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs12.x"
  memory_size   = 128
  timeout       = 1
}
