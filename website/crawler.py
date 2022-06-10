from constructs import Construct
from aws_cdk import Duration
from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_solutions_constructs.aws_s3_sqs import S3ToSqs
from aws_solutions_constructs.aws_sqs_lambda import SqsToLambda


PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_9


class S3MicroformatsCrawler(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        timezone,
        date_format="%A, %B %-d",
        time_format="%-I:%-M %p",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.table = dynamodb.Table(
            self,
            "CrawlerTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        self.table.add_local_secondary_index(
            sort_key=dynamodb.Attribute(
                name="LSI1SK", type=dynamodb.AttributeType.STRING
            ),
            index_name="LSI1",
        )

        self.s3_to_sqs = S3ToSqs(   
            self,
            "BucketEventsToCrawlerQueue",
            existing_bucket_obj=bucket,
            s3_event_filters=[{"suffix": "html"}],
           s3_event_types=[s3.EventType.OBJECT_CREATED, s3.EventType.OBJECT_REMOVED],
        )

        self.crawl_function = lambda_python.PythonFunction(
            self,
            "CrawlS3Function",
            entry="function_code/crawler",
            handler="lambda_handler",
            runtime=PYTHON_RUNTIME,
            timeout=Duration.seconds(20),
            environment={
                "TZ": timezone,
                "DATE_FORMAT": date_format,
                "TIME_FORMAT": time_format,
                "TABLE": self.table.table_arn,
            },
        )

        self.sqs_to_lambda = SqsToLambda(
            self,
            "ProcessCrawlerSqsToLambda",
            existing_lambda_obj=self.crawl_function,
            existing_queue_obj=self.s3_to_sqs.sqs_queue,
        )

        bucket.grant_read(self.sqs_to_lambda.lambda_function)
        self.table.grant_read_write_data(self.sqs_to_lambda.lambda_function)
