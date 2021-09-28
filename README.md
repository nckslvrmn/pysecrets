pysecrets
===

A light-weight, ephemeral secret sharing service. pysecrets uses a secure PBKDF and the latest AES encryption standards to ensure the confidentiality, integrity, and authenticity of data sent through the service. Pysecrets is intended to run in AWS as a serverless application, with a static UI hosted in an S3 bucket.

## Dependencies

Pysecrets requires python3.9, the [cryptography](https://pypi.org/project/cryptography/) module, and [boto3](https://pypi.org/project/boto3/) (included in the lambda runtime already), to support the mode of encryption used by the service.

Pysecrets uses AWS serverless services including: Lambda, DynamoDB, Api Gateway, and S3. These are used for the application runtime and UI, as well as storage of encrypted secrets.

All the terraform necessary to create the infrastructure required to run a copy of the application is included in the `terraform/` directory.

## Installation

1. The first step is to run the provided terraform in your AWS account. This directory can be sourced as a terraform module and the variables defined can be passed in. [Here's a link](https://www.terraform.io/docs/language/modules/index.html) for more information on that.
2. Once the infrastructure has been set up, run `make` to build the Lambda function zip file that will be uploaded to AWS.
3. From there upload it using this command `aws lambda update-function-code --function-name secrets --zip-file fileb://function.zip`.
4. Lastly, run `aws s3 cp --region us-east-1 static/ s3://BUCKET_NAME` to upload the UI to the site bucket terraform created.

## Configuration

To ensure the best security practices, the methods used for KDF and encryption/decryption have been baked into the code itself.
There are a few options that can be configured. All of these should be passed in to the function via environment variables.

VARIABLE     | DEFAULT | DESCRIPTION
-------------|---------|---------------------------------------------------------
TTL_DAYS     | 5       | Configures the TTL that the secret records will have in Dynamo.
S3_BUCKET    | nil     | Tells the server in which S3 bucket to store encrypted files.

If using the provided terraform, `TTL_DAYS` is an option that can be passed in, and `S3_BUCKET` is predefined with the proper value.

## API Usage

Because pysecrets uses the SPA + API architecture, the APIs can be accessed directly. To interact with the APIs, here are some examples via CURL. To send and receive a string based secret:
```
~ ❯ curl -X POST https://URL/encrypt -d '{"secret": "super secret text", "view_count": 1}'
{"secret_id": "HrVfOn1aoqKHeRKi", "passphrase": "iT95_B9p9PSMcP-hH9OGS81w9FZVTEpf"}

~ ❯ curl -X POST https://URL/decrypt -d '{"secret_id": "HrVfOn1aoqKHeRKi", "passphrase": "iT95_B9p9PSMcP-hH9OGS81w9FZVTEpf"}'
{"data": "super secret text"}
```
The string based secret sharing works by passing the `encrypt` route secret text and a view count via a JSON payload. To retreive the secret, send the `decrypt` route the generated secret id and passphrase.

The file based API works similarly:
```
~ ❯ cat test.txt
hello

~ ❯ curl -X POST "https://URL/encrypt?file_name=test.txt" -d '@test.txt'
{"secret_id": "97tfNQQBAl0w2zNE", "passphrase": "CPIX4PeLALaLaNLVFM~oNjM!N&bjZ377"}

~ ❯ curl -X POST https://URL/decrypt -d '{"secret_id": "97tfNQQBAl0w2zNE", "passphrase": "CPIX4PeLALaLaNLVFM~oNjM!N&bjZ377"}'
{"data": "aGVsbG8=", "file_name": "test.txt"}

~ ❯ echo "aGVsbG8=" | base64 -d
hello
```
The same `encrypt` route is used but this time, the data payload is the file to encrypt. Additionally, a `file_name` url parameter is specified that determines the file name that the receiver will use to write the received file. To retrieve this file, hit the same `decrypt` route with the same payload as the string secret. This will return a JSON object containing the output file name an a base64 encoded string of the files original contents. Decode the data string and write it to a file for storage. The UI will handle all of that should that be used.

## Security Features

Ephemeral Secret service utilizes the best in business algorithms and functions for proper encryption at rest that guarantees information security. There is another domain of security however not covered by the service itself. That is encryption in transit. As previously mentioned, an nginx configuration file is provided that can serve as the web server proxy. It is highly reccomended to follow or use this configuration as it contains all the options required for modern best practices on encryption in transit. When configuring these best practice options, there is a somewhat significant reduction in comptibility for older devices but considering the security gains this is a worthwhile sacrifice.

Pysecrets uses three main security standards to ensure full information security.

### AES

The first of which is the encryption/decryption mode. Pysecrets uses `AES-256-GCM`. This uses the AES standard with a key size of 256 bits and the GCM mode. GCM is a combination of Galois field authentication and a counter mode algorithm and can be further documented [here](https://en.wikipedia.org/wiki/Galois/Counter_Mode).
GCM was designed to be performant (via parallelized operations) and to guarantee authenticity and confidentiality. By using an AEAD (authenticated encryption with associated data) cipher mode, one can guarantee that the ciphertext maintains integrity upon decryption and will fail to decrypt if someone attempts to modify the ciphertext while it remains encrypted.

### Scrypt

Scrpyt is a password-based key derivation function and us used to generate the AES key used for encryption and decryption. Scrypt was designed to take input paramaters that relate largely to the hardware resources available. Because it uses the most resources available to it, brute force or custom hardware attacks become infeasible. More on the function can be read [here](https://en.wikipedia.org/wiki/Scrypt).

### Random Strings

Pythons `os` package comes with functions that allow for access to random number generation from the `/dev/urandom` entropy pool device.

## Licensing

This project is licensed under the terms of the MIT License.
