# Indeed Scraper

This repository scrapes Indeed for job listings that match specified keywords and automatically emails the results to configured recipients on a scheduled basis.

This project uses AWS CDK v2 (Python) to deploy a scheduled Lambda function with dependencies managed via a Lambda Layer.

## Project Structure

- `src/` - Lambda function code (e.g., `main.py` with a `handler` function)
- `lambda_layer/requirements.txt` - Python dependencies for Lambda Layer (e.g., `requests`)
- `app.py` - CDK app and stack definition
- `cdk.json` - Project-level configuration for the AWS CDK CLI

## Prerequisites

- Python 3.9+
- AWS CLI configured with your credentials (e.g., `~/.aws/credentials`)
- AWS CDK v2 CLI (`npm install -g aws-cdk`)
- Docker (must be running for CDK bundling)

## Setup

1. **Install Python dependencies:**

   ```sh
   pip install -r requirements.txt
   pip install aws-cdk-lib constructs
   ```

2. **Set your AWS profile (if not using default):**

   ```sh
   export AWS_PROFILE=<your-aws-profile>
   ```

3. **Install the AWS CLI (if not already installed):**

   Follow the [official AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) or use:

   ```sh
   pip install awscli
   ```

4. **Configure your AWS credentials (if not already configured):**

   You can set up your credentials using the AWS CLI:

   ```sh
   aws configure
   ```

   This will prompt you for your AWS Access Key ID, Secret Access Key, region, and output format, and store them in `~/.aws/credentials` and `~/.aws/config`.

5. **Create required SSM parameters:**

   Replace the example names and values as needed:

   ```sh
   aws ssm put-parameter --name "/indeed-scraper/api-key" --value "your-api-key" --type "SecureString"
   aws ssm put-parameter --name "/indeed-scraper/sender_email" --value "<verified SES Identity>" --type "SecureString"
   aws ssm put-parameter --name "/indeed-scraper/receiver_email" --value "<Verified SES Identity>" --type "SecureString"
   ```

   These parameters will be used by the Lambda function at runtime.

6. **Bootstrap your AWS environment for CDK (if not previously performed for AWS Account):**

   ```sh
   cdk bootstrap
   ```

7. **Deploy the stack:**
   ```sh
   cdk deploy
   ```

## Notes on Lambda Layers and Docker

- **Dependencies:** Place all Python dependencies for your Lambda in `lambda_layer/requirements.txt`.
- **CDK Bundling:** CDK uses Docker to build the Lambda Layer so dependencies are compatible with the Lambda runtime. **Docker must be installed and running locally** for this to work.
- **No manual zipping required:** CDK handles packaging and uploading both your Lambda code and the layer.
- **Keep code and dependencies separate:** Your application code stays in `src/`, dependencies in `lambda_layer/`.

## Troubleshooting

- If you see errors about Docker, ensure Docker Desktop is running.
- If you see errors about missing SSM parameters or roles, make sure you have run `cdk bootstrap`.
- If you see errors about credentials, ensure your AWS profile is set correctly.

## Useful Commands

- Synthesize CloudFormation template: `cdk synth`
- Deploy stack: `cdk deploy`
- Destroy stack: `cdk destroy`

## Running Unit Tests

Unit tests are located in the `tests/` directory. To run all tests, use:

```sh
python -m unittest discover -s tests
```

Or to run a specific test file:

```sh
python -m unittest tests/test_main.py
```

Make sure you run these commands from the project root (where `src/` and `tests/` are located) and that both `src/` and `tests/` contain an `__init__.py` file to enable package-style imports.

Make sure you have the required dependencies installed (see `requirements.txt`).

## References

- [AWS CDK Python API Reference](https://docs.aws.amazon.com/cdk/api/v2/python/index.html)
- [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [CDK Bundling](https://docs.aws.amazon.com/cdk/v2/guide/bundling.html)
