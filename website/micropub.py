import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import pytz
from aws_cdk import Duration
from aws_cdk import aws_apigatewayv2_alpha as apigwv2
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_s3 as s3
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from constructs import Construct

PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_9


class MicropubApi(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        template_bundle,
        timezone,
        token_endpoint,
        me_url,
        author_name,
        authorizer,
        date_format="%A, %B %-d",
        time_format="%-I:%-M %p",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigwv2.HttpApi(self, "MicropubApi", default_authorizer=authorizer)

        micropub_clean_function = lambda_python.PythonFunction(
            self,
            "MicropubCleanFunction",
            entry="function_code/micropub_clean",
            handler="lambda_handler",
            runtime=PYTHON_RUNTIME,
            timeout=Duration.seconds(20),
            environment={
                "BUCKET": bucket.bucket_name,
                "TEMPLATE_BUCKET": template_bundle.s3_bucket_name,
                "TEMPLATE_BUNDLE_KEY": template_bundle.s3_object_key,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
                "AUTHOR_NAME": author_name,
                "TZ": timezone,
                "DATE_FORMAT": date_format,
                "TIME_FORMAT": time_format,
            },
        )
        bucket.grant_read_write(micropub_clean_function)

        micropub_proxy_function = lambda_python.PythonFunction(
            self,
            "MicropubProxyFunction",
            entry="function_code/micropub_proxy",
            handler="lambda_handler",
            runtime=PYTHON_RUNTIME,
            timeout=Duration.seconds(20),
            environment={
                "MICROPUB_CLEAN": self.api.url + "micropub-clean",
                "MICROPUB_MEDIA": self.api.url + "micropub-media",
            },
        )

        micropub_get_function = lambda_python.PythonFunction(
            self,
            "MicropubGetFunction",
            entry="function_code/micropub_get",
            handler="lambda_handler",
            runtime=PYTHON_RUNTIME,
            environment={
                "BUCKET": bucket.bucket_name,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
                "MEDIA_ENDPOINT": self.api.url + "micropub-media",
            },
        )

        micropub_media_function = lambda_python.PythonFunction(
            self,
            "MicropubMediaFunction",
            entry="function_code/micropub_media",
            handler="lambda_handler",
            runtime=PYTHON_RUNTIME,
            environment={
                "BUCKET": bucket.bucket_name,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
            },
        )

        self.api.add_routes(
            path="/micropub",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration(
                "MicropubProxyIntegration", micropub_proxy_function
            ),
            authorizer=apigwv2.HttpNoneAuthorizer(),
        )

        self.api.add_routes(
            path="/micropub-clean",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration(
                "MicropubCleanIntegration", micropub_clean_function
            ),
        )
        self.api.add_routes(
            path="/micropub",
            methods=[apigwv2.HttpMethod.GET],
            integration=HttpLambdaIntegration(
                "MicropubGetIntegration", micropub_get_function
            ),
        )

        self.api.add_routes(
            path="/micropub-media",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration(
                "MicropubMediaIntegration", micropub_media_function
            ),
        )

        template_bundle.grant_read(micropub_clean_function)
        bucket.grant_write(micropub_media_function)
