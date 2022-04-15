from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
)

import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
from aws_cdk.aws_s3_assets import Asset

from constructs import Construct
import pytz

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
        feed_bucket = s3.Bucket(
            self, "FeedsBucket", website_index_document="index.html"
        )
        content_bucket = s3.Bucket(
            self, "PostsBucket", website_index_document="index.html"
        )

        hosted_zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain)

        template_bundle = Asset(self, "MicropubTemplateBundle",
            path = 'templates'
        )


        micropub = MicropubApi(
            self,
            "micropub",
            timezone="US/Eastern",
            bucket=content_bucket,
            template_bundle = template_bundle,
            token_endpoint="https://tokens.indieauth.com/token",
            me_url="https://" + domain,
            author_name="Ross M Karchner"
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

        cdn = CdnWithDNSAndCert(
            self,
            "CDNWithDNSAndCert",
            hosted_zone=hosted_zone,
            domain_names=[domain],
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(content_bucket),
                function_associations=[
                    {
                        "function": cf_function,
                        "eventType": cloudfront.FunctionEventType.VIEWER_RESPONSE,
                    }
                ],
            ),
        )

        cdn.distribution.add_behavior("/feeds/*", origins.S3Origin(feed_bucket))