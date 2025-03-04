import pulumi

import pulumi_aws

ssh_sg = pulumi_aws.ec2.SecurityGroup('ssh-access-sg',
    name='ssh-access-sg',
    description='Security group for accessing by SSH',
    ingress=['allow-ssh-access']
)

pulumi_aws.vpc.SecurityGroupIngressRule('allow-ssh-access',
    security_group_id=ssh_sg.id,
    cidr_ipv4='0.0.0.0/0',
    from_port=22,
    ip_protocol='tcp',
    to_port=22
)
