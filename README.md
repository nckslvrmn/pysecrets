pysecrets
===

A light-weight, ephemeral secret sharing service. Secrets uses the latest AES and KDF encryption standards to ensure the confidentiality, integrity, and authenticity of data sent through the service.

## Getting Started

Secrets requires python3.8 and PyCryptodome to support the mode of encryption used by the service.
Secrets is also intended to run as AWS Lambda functions, with a static UI hosted in a place of your choosing.

## Dependencies

Secrets uses an AWS Dynamo DB table for storing all of its string secrets and an S3 bucket for encrypted files. Secrets requires that the role the Lambda executes with has the proper permissions to the Dynamo Table and S3 Bucket.
The Dynamo table and S3 Bucket need to exist beforehand.

## Installation

Once the dependencies have been set up, begin by running `make function`.
This will build the Lambda function zip file that will be uploaded to AWS.

## Configuration

To ensure the best security practices, the methods used for KDF and encryption/decryption have been baked into the code itself.
There are a few options that can be configured. All of these should be passed in to the functions.

Within the environments hash, the options are:

VARIABLE     | DEFAULT | DESCRIPTION
-------------|---------|---------------------------------------------------------
TTL_DAYS     | 5       | Configures the TTL that the secret records will have in Dynamo.
S3_BUCKET    | nil     | Tells the server in which S3 bucket to store encrypted files.


## Security Features

Ephemeral Secret service utilizes the best in business algorithms and functions for proper encryption at rest that guarantees information security. There is another domain of security however not covered by the service itself. That is encryption in transit. As previously mentioned, an nginx configuration file is provided that can serve as the web server proxy. It is highly reccomended to follow or use this configuration as it contains all the options required for modern best practices on encryption in transit. When configuring these best practice options, there is a somewhat significant reduction in comptibility for older devices but considering the security gains this is a worthwhile sacrifice.

Ephemeral Secrets uses three main security standards to ensure full information security.

### AES

The first of which is the encryption/decryption mode. Secrets uses `AES-256-GCM`. This uses the AES standard with a key size of 256 bits and the GCM mode. GCM is a combination of Galois field authentication and a counter mode algorithm and can be further documented [here](https://en.wikipedia.org/wiki/Galois/Counter_Mode).
GCM was designed to be performant (via parallelized operations) and to guarantee authenticity and confidentiality. By using an AEAD (authenticated encryption with associated data) cipher mode, one can guarantee that the ciphertext maintains integrity upon decryption and will fail to decrypt if someone attempts to modify the ciphertext while it remains encrypted.

### Scrypt

Scrpyt is a password-based key derivation function and us used to generate the AES key used for encryption and decryption. Scrypt was designed to take input paramaters that relate largely to the hardware resources available. Because it uses the most resources available to it, brute force or custom hardware attacks become infeasible. More on the function can be read [here](https://en.wikipedia.org/wiki/Scrypt).

### Random Strings

Pycryptodomes Random module is used to generate both random IDs for the secrets to be stored as well as random passwords. It supports random number generation the `/dev/urandom` entropy pool device. More on that can be found [here](https://pycryptodome.readthedocs.io/en/latest/src/random/random.html)

## Licensing

This project is licensed under the terms of the MIT License.
