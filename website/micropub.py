from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_apigatewayv2_alpha as apigwv2,
    aws_lambda as lambda_,
    aws_ecr_assets as ecr_assets,
    aws_lambda_python_alpha as lambda_python,
)


import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins

from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration


from constructs import Construct

import pytz


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
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigwv2.HttpApi(self, "MicropubApi")

        micropub_post_function = lambda_python.PythonFunction(
            self,
            "MicropubPostFunction",
            entry="function_code/micropub_post",
            handler="micropub_post",
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=Duration.seconds(20),
            environment={
                "BUCKET": bucket.bucket_name,
                "TEMPLATE_BUCKET": template_bundle.s3_bucket_name,
                "TEMPLATE_BUNDLE_KEY": template_bundle.s3_object_key,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
                "AUTHOR_NAME": author_name,
                "TZ": timezone,
            },
        )


        micropub_get_function = lambda_python.PythonFunction(
            self,
            "MicropubGetFunction",
            entry="function_code/micropub_get",
            handler="micropub_get",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment={
                "BUCKET": bucket.bucket_name,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
            },
        )

        micropub_media_function = lambda_python.PythonFunction(
            self,
            "MicropubMediaFunction",
            entry="function_code/micropub_media",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment={
                "BUCKET": bucket.bucket_name,
                "TOKEN_ENDPOINT": token_endpoint,
                "ME_URL": me_url,
            },  
        )

        micropub_post_intergation = HttpLambdaIntegration(
            "MicropubPostIntegration", micropub_post_function
        )

        micropub_get_intergation = HttpLambdaIntegration(
            "MicropubGetIntegration", micropub_get_function
        )

        micropub_media_intergation = HttpLambdaIntegration(
            "MicropubGetIntegration", micropub_get_function
        )

        self.api.add_routes(
            path="/micropub",
            methods=[apigwv2.HttpMethod.POST],
            integration=micropub_post_intergation,
        )
        self.api.add_routes(
            path="/micropub",
            methods=[apigwv2.HttpMethod.GET],
            integration=micropub_get_intergation,
        )

        self.api.add_routes(
            path="/micropub-media",
            methods=[apigwv2.HttpMethod.POST],
            integration=micropub_media_intergation,
        )

        template_bundle.grant_read(micropub_post_function)
