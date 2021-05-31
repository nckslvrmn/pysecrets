resource "aws_dynamodb_table" "secrets" {
  name         = "Secrets"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "secret_id"

  attribute {
    name = "secret_id"
    type = "S"
  }

  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = {
    Name = "Secrets"
  }
}
