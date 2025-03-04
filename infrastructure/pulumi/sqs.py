import pulumi

from pulumi_aws import sqs

sqs.Queue('telephone', name='telephone')
