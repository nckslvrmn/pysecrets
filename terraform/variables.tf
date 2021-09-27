variable "ttl_days" {
  type    = string
  default = "7"
}

variable "hosted_zone_id" {
  type = string
}

variable "domain_name" {
  type = string
}


variable "acm_arn" {
  type = string
}

variable "prefix" {
  type = string
}
