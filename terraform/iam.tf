data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "edgelamnda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "bucket_access" {
  statement {
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.secrets_files.arn,
      "${aws_s3_bucket.secrets_files.arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "dynamo_access" {
  statement {
    actions   = ["dynamodb:*"]
    resources = [aws_dynamodb_table.secrets.arn]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "s3_bucket" {
  name   = "s3_bucket"
  role   = aws_iam_role.iam_for_lambda.id
  policy = data.aws_iam_policy_document.bucket_access.json
}

resource "aws_iam_role_policy" "dynamo_table" {
  name   = "dynamo_table"
  role   = aws_iam_role.iam_for_lambda.id
  policy = data.aws_iam_policy_document.dynamo_access.json
}
