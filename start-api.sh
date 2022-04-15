#!/usr/bin/env bash

cdk synth --no-staging > template.yml && sam local start-api