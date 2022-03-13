#!/usr/bin/env python3
import os

import aws_cdk as cdk

from website.website_stack import WebsiteStack
env = cdk.Environment(account="797438674243", region="us-east-1")

app = cdk.App()
WebsiteStack(app, "WebsiteStack", env=env, domain='ross.karchner.com'
    )

app.synth()
