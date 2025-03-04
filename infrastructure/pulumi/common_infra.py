import pulumi

import pulumi_aws as aws

ssh_sg = aws.ec2.SecurityGroup('ssh-access-sg',
    name='ssh-access-sg',
    description='Security group for accessing by SSH'
)

aws.vpc.SecurityGroupIngressRule('allow-ssh-access',
    security_group_id=ssh_sg.id,
    ip_protocol='tcp',
    cidr_ipv4='0.0.0.0/0',
    from_port=22,
    to_port=22
)

pulumi.export('ssh_access_sg_id', ssh_sg.id)
