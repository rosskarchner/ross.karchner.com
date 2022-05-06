from aws_cdk import aws_logs as logs
from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    AwsSdkCall,
    PhysicalResourceId,
)
from constructs import Construct


class FileToBucket(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bucket_name: str,
        file_name: str,
        file_contents: str,
    ):
        super().__init__(scope, id)
        self.file_name = file_name
        self.file_contents = file_contents
        res = AwsCustomResource(
            scope=self,
            id="AWSCustomResource",
            policy=AwsCustomResourcePolicy.from_sdk_calls(
                resources=[f"arn:aws:s3:::{bucket_name}/*"]
            ),
            log_retention=logs.RetentionDays.INFINITE,
            on_create=self.create(bucket_name),
            on_delete=self.delete(bucket_name),
            on_update=self.create(bucket_name),
            resource_type="Custom::MyCustomResource",
        )

    def create(self, bucket_name):

        create_params = {
            "Body": self.file_contents,
            "Bucket": bucket_name,
            "Key": self.file_name,
            "ContentType": "text/html"
        }

        return AwsSdkCall(
            action="putObject",
            service="S3",
            parameters=create_params,
            physical_resource_id=PhysicalResourceId.of("myAutomationExecution"),
        )

    def delete(self, bucket_name):

        delete_params = {"Bucket": bucket_name, "Key": self.file_name}

        return AwsSdkCall(
            action="deleteObject",
            service="S3",
            parameters=delete_params,
            physical_resource_id=PhysicalResourceId.of("myAutomationExecution"),
        )
