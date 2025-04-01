import pulumi

import pulumi_aws as aws


common_infra = pulumi.StackReference('ZaiusDR/common_infra/live')

vault_sg = aws.ec2.SecurityGroup(
    resource_name='vault-sg',
    name='vault-sg',
    description='Security group for Vault Server',
    egress=[{
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": ["0.0.0.0/0"]
    }]
)

aws.vpc.SecurityGroupIngressRule(
    resource_name='allow-vault-access',
    security_group_id=vault_sg.id,
    ip_protocol='tcp',
    cidr_ipv4=common_infra.get_output('default_vpc')['cidr_block'],
    from_port=8200,
    to_port=8200,
)

vault_instance = aws.ec2.Instance(
    resource_name='vault',
    ami=common_infra.get_output('ami_id'),
    instance_type=aws.ec2.InstanceType.T3A_MICRO,
    key_name=common_infra.get_output('key_pair')['key_name'],
    vpc_security_group_ids=[common_infra.get_output('ssh_access_sg_id'), vault_sg.id],
    availability_zone='eu-west-3a',
    iam_instance_profile='vault-server',
    tags={
        'Name': 'vault',
        'Role': 'vault'
    }
)

vault_volume = aws.ebs.Volume(
    resource_name='vault-volume',
    availability_zone='eu-west-3a',
    encrypted=True,
    size=2,
    type='gp3',
    final_snapshot=False,
    tags={
        'Name': 'vault-volume'
    }
)

aws.ec2.VolumeAttachment(
    resource_name='vault-volume-attachment',
    device_name="/dev/xvdf",
    volume_id=vault_volume.id,
    instance_id=vault_instance.id
)

aws.kms.Key(
    resource_name='vault-auto-unseal',
    description='Vault Auto-Unseal Key',
    bypass_policy_lockout_safety_check=False,
    tags={
        'Name': 'vault-auto-unseal'
    }
)

hosted_zone = aws.route53.get_zone(name='esuarez.info.', private_zone=True)

aws.route53.Record(
    resource_name='vault-private-record',
    zone_id=hosted_zone.id,
    name='vault.esuarez.info',
    type=aws.route53.RecordType.A,
    ttl=300,
    records=[vault_instance.private_ip]
)

pulumi.export('vault_private_ip', vault_instance.private_ip)
