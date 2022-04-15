import os
import pathlib
import tempfile
import zipfile

import boto3
import chevron
import mf2util

s3 = boto3.client("s3")
_, local_bundle_file = tempfile.mkstemp(suffix=".zip")
s3.download_file(
    Bucket=os.environ["TEMPLATE_BUCKET"],
    Key=os.environ["TEMPLATE_BUNDLE_KEY"],
    Filename=local_bundle_file,
)

local_template_dir = tempfile.mkdtemp()
zipfile.ZipFile(local_bundle_file).extractall(path=local_template_dir)


template_path = pathlib.Path(local_template_dir)
default_template = template_path / "hentry.mustache"


def document_to_html(document):
    post_type = mf2util.post_type_discovery(document)
    post_url = document["properties"]["url"][0]
    template_for_post_type = template_path / ("hentry.%s.mustache" % post_type)
    if template_for_post_type.exists():
        template = template_for_post_type.open().read()
    else:
        template = default_template.open().read()

    context = mf2util.interpret_entry(
        {
            "items": [
                document,
            ]
        },
        source_url=post_url,
    )
    return chevron.render(template, context, partials_path=template_path)
