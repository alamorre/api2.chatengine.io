## Building the Docker images

There are two images:

- `api.chatengine.io` which handles all the API calls
- `ws.chatengine.io` which handles all the websocket connections

Luckily, this repo has GitHub actions for building and pushing both images into ECR.

Here are the steps to build and deploy your images:

1. Create your own GitHub repo for this codebase
2. Setup Secrets -> Actions with the values: `AWS_ACCESS_KEY_ID`, `AWS_REGION`, `AWS_SECRET_ACCESS_KEY` and `SEND_GRID_KEY` (only add the sengrid one if you plan to run unit tests)
3. Setup an ECR registry in the AWS console.
4. Run the GitHub actions under "Actions > (Push) api.chatengine.io" and "Actions > (Push) ws.chatengine.io"

## Deploy to AWS with terraform

ChatEngine is deployed to AWS with terraform.

To start, make sure the AWS CLI and TerraForm CLI are installed. Second, make sure you have an AWS account with a `AWS_ACCESS_KEY_ID`, `AWS_REGION`, `AWS_SECRET_ACCESS_KEY` and `ZONE_ID`.

These will be needed to set the environment variables before you deploy.

## Environment Variables

Make your own file called `terraform/aws/terraform.tfvars` and add the following values.

(You'll need to get your own keys for AWS, Sendgrid and Sentry. Also enter your own names as described below.)

```
aws_access_key_id        = "AKIA..."
aws_secret_access_key    = "...
aws_storage_bucket_name  = "make-your-own-unique-name"
db_name                  = "make-your-own-db-name"
db_username              = "make-your-own-username"
db_password              = "make-your-own-random-string"
domain_name              = "api2.chatengine.io"
pipeline                 = "production"
redis_host               = "redis"
redis_port               = "6379"
secret_key               = "make-your-own-random-string"
send_grid_key            = "SG.T3_YaV..."
sentry_dsn_api           = "..."
sentry_dsn_ws            = "..."
stripe_key               = "..."
stripe_light_plan        = "..."
stripe_production_plan   = "..."
stripe_professional_plan = "..."
stripe_tax_rate          = "..."
zone_id                  = "Z08425162ICSXXTKGQ6L1"
```

## Running Terraform to deploy

With this all in place, you're now ready to run terraform!

```
cd terraform/aws
terraform init # to install the providers
terraform apply
```

Specify the image tags (assuming you ran the GitHub actions to publish to your ECR registry). You can also specify `latest` for both images.

Boom, you're done!
