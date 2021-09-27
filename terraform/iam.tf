# lambda role
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

data "aws_iam_policy_document" "bucket_access" {
  statement {
    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = ["${aws_s3_bucket.secrets_files.arn}/*"]
  }
}

data "aws_iam_policy_document" "dynamo_access" {
  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.secrets.arn]
  }
}

resource "aws_iam_role" "secrets" {
  name               = "secrets_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "basic_exec" {
  role       = aws_iam_role.secrets.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "s3_bucket" {
  name   = "s3_bucket"
  role   = aws_iam_role.secrets.id
  policy = data.aws_iam_policy_document.bucket_access.json
}

resource "aws_iam_role_policy" "dynamo_table" {
  name   = "dynamo_table"
  role   = aws_iam_role.secrets.id
  policy = data.aws_iam_policy_document.dynamo_access.json
}


# api gateway role
data "aws_iam_policy_document" "apigateway_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "apigateway.amazonaws.com",
      ]
    }
  }
}

data "aws_iam_policy_document" "apigateway_bucket_access" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.secrets_site.arn}/*"]
  }
}

resource "aws_iam_role" "apigateway" {
  name               = "secrets_apigateway_role"
  assume_role_policy = data.aws_iam_policy_document.apigateway_assume.json
}

resource "aws_iam_role_policy" "apigateway_s3_bucket" {
  name   = "s3_bucket"
  role   = aws_iam_role.apigateway.id
  policy = data.aws_iam_policy_document.apigateway_bucket_access.json
}
