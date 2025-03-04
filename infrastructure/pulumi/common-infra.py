import pulumi
from ansible_collections.ansible.utils.plugins.filter.cidr_merge import cidr_merge

from pulumi_aws import ec2

ec2.SecurityGroup('ssh-access-sg',
    name='ssh-access-sg',
    description='Security group for accessing by SSH',
    ingress=['allow-ssh-access']
)

ec2.SecurityGroupIngressRule('allow-ssh-access',
    protocol='tcp',
    from_port=22,
    to_port=22,
    cidr_blocks=['0.0.0.0/0']
)
