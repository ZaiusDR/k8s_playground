import pulumi

import pulumi_aws as aws

config = pulumi.Config()

ubuntu_ami_id_ssm_path = config.require('ubuntuAmiIdSSMPath')
ami_id = aws.ssm.get_parameter(name=ubuntu_ami_id_ssm_path)

key_pair = aws.ec2.get_key_pair(key_name='k8s-cluster-key-pair')

default_vpc = aws.ec2.get_vpc(default=True)

ssh_sg = aws.ec2.SecurityGroup(
    resource_name='ssh-access-sg',
    name='ssh-access-sg',
    description='Security group for accessing by SSH'
)

aws.vpc.SecurityGroupIngressRule(
    resource_name='allow-ssh-access',
    security_group_id=ssh_sg.id,
    ip_protocol='tcp',
    cidr_ipv4='0.0.0.0/0',
    from_port=22,
    to_port=22
)

pulumi.export('ami_id', ami_id.value)
pulumi.export('default_vpc', default_vpc)
pulumi.export('key_pair', key_pair)
pulumi.export('ssh_access_sg_id', ssh_sg.id)
