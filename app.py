from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Stack,
    Duration,
    App
)
from constructs import Construct

class ScrapeIndeedJobsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer for dependencies (CDK v2 compliant)
        layer = _lambda.LayerVersion(
            self, "RequestsLayer",
            code=_lambda.Code.from_asset(
                path="lambda_layer",
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output/python"
                    ]
                }
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Lambda layer with requests dependency"
        )

        # Lambda execution role
        lambda_role = iam.Role(
            self, "ScrapeIndeedJobsLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=[
                    "arn:aws:ses:us-east-1:748195683236:identity/*"
                ]
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
            actions=[
                "ssm:GetParameter",
                "ssm:GetParameters"
            ],
            resources=[
                "arn:aws:ssm:us-east-1:748195683236:parameter/indeed-scraper/api_key",
                "arn:aws:ssm:us-east-1:748195683236:parameter/indeed-scraper/sender_email",
                "arn:aws:ssm:us-east-1:748195683236:parameter/indeed-scraper/receiver_email"
            ]
            )
        )

        # Lambda function
        lambda_fn = _lambda.Function(
            self, "ScrapeIndeedJobsLambda",
            function_name="scrape-indeed-jobs",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=_lambda.Code.from_asset("src"),
            role=lambda_role,
            timeout=Duration.seconds(300),
            memory_size=256,
            layers=[layer]
        )

        # Scheduled EventBridge rule
        rule = events.Rule(
            self, "ScrapeIndeedJobsSchedule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="15,18,21,0",
            )
        )
        rule.add_target(targets.LambdaFunction(lambda_fn))

app = App()
ScrapeIndeedJobsStack(app, "ScrapeIndeedJobsStack")
app.synth()