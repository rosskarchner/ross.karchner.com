from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from aws_cdk import aws_s3 as s3  # Duration,
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk.aws_s3_assets import Asset
from aws_cdk.aws_apigatewayv2_authorizers_alpha import (
    HttpLambdaAuthorizer,
    HttpLambdaResponseType,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
from constructs import Construct

from .bucket_file import FileToBucket
from .micropub import MicropubApi


class CdnWithDNSAndCert(Construct):
    """Cloudfront Distro, with Route53 and ACM Cert"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        hosted_zone: route53.HostedZone,
        default_behavior: cloudfront.BehaviorOptions,
        domain_names: list,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cert = acm.Certificate(
            self,
            "Certificate",
            domain_name=domain_names[0],
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        self.distribution = cloudfront.Distribution(
            self,
            "CDN",
            domain_names=domain_names,
            default_behavior=default_behavior,
            default_root_object="index.html",
            certificate=cert,
        )

        ipv4 = route53.ARecord(
            self,
            "ipv4Arecord",
            zone=hosted_zone,
            record_name=domain_names[0],
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            ),
        )

        ipv6 = route53.AaaaRecord(
            self,
            "ipv6Arecord",
            zone=hosted_zone,
            record_name=domain_names[0],
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            ),
        )


class WebsiteStack(Stack):
    """The Website"""

    def __init__(self, scope: Construct, construct_id: str, domain, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        feed_bucket = s3.Bucket(self, "FeedsBucket")
        content_bucket = s3.Bucket(self, "PostsBucket")

        hosted_zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain)

        template_bundle = Asset(self, "MicropubTemplateBundle", path="templates")

        indieauth_token_authorizer_function = lambda_python.PythonFunction(
            self,
            "IndieAuthTokenAuthorizerFunction",
            entry="function_code/authorize",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(20),
            environment={
                "UPSTREAM_TOKEN_ENDPOINT": "https://tokens.indieauth.com/token",
                "ME_URL": "https://" + domain + "/",
            },
        )

        authorizer = HttpLambdaAuthorizer(
            "IndieAuthTokenAuthorizer",
            indieauth_token_authorizer_function,
            response_types=[HttpLambdaResponseType.SIMPLE],
            identity_source=["$request.header.Authorization"],
            results_cache_ttl=Duration.minutes(10),
        )

        index_html = FileToBucket(
            self,
            "IndexHtml",
            feed_bucket.bucket_name,
            file_name="index.html",
            file_contents=open("placeholder.html").read(),
        )

        micropub = MicropubApi(
            self,
            "micropub",
            timezone="US/Eastern",
            bucket=content_bucket,
            template_bundle=template_bundle,
            token_endpoint="https://tokens.indieauth.com/token",
            me_url="https://" + domain + "/",
            author_name="Ross M Karchner",
            authorizer=authorizer,
        )

        cf_function_code = """
        function handler(event) {
            var response = event.response;
            var headers = response.headers;

            headers['link'] = { 
                "value": 'https://indieauth.com/auth; rel=authorization_endpoint',
                multiValue: [ 
                    {"value": 'https://indieauth.com/auth; rel=authorization_endpoint'},
                    {"value": 'https://tokens.indieauth.com/token; rel=token_endpoint'},
                    {"value": '%smicropub; rel=micropub'},
                ]
            
            
            }; 

            // Return the response to viewers 
            return response;
        }
        """ % (
            micropub.api.url
        )

        cf_function = cloudfront.Function(
            self, "Function", code=cloudfront.FunctionCode.from_inline(cf_function_code)
        )

        oai = cloudfront.OriginAccessIdentity(self, "WebsiteOriginAccessIdentity")

        cdn = CdnWithDNSAndCert(
            self,
            "CDNWithDNSAndCert",
            hosted_zone=hosted_zone,
            domain_names=[domain],
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(content_bucket, origin_access_identity=oai),
            ),
        )
        # Can I do this in one statement?
        cdn.distribution.add_behavior(
            "/feeds/*", origins.S3Origin(feed_bucket, origin_access_identity=oai)
        )
        cdn.distribution.add_behavior(
            "index.html",
            origins.S3Origin(feed_bucket, origin_access_identity=oai),
            function_associations=[
                {
                    "function": cf_function,
                    "eventType": cloudfront.FunctionEventType.VIEWER_RESPONSE,
                }
            ],
        )

        feed_bucket.grant_read(oai)
        content_bucket.grant_read(oai)
