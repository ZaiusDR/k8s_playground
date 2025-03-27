import pulumi

import pulumi_aws as aws


HA_PROXY_PORTS = {'http': 80, 'https': 443, 'k8s-api': 6443}
SUBDOMAINS = [
    'argocd',
    'guestbook',
    'k8s',
    'producer-front',
    'producer-back',
    'consumer-front',
    'consumer-back'
]

common_infra = pulumi.StackReference('ZaiusDR/common_infra/live')

ha_proxy_sg = aws.ec2.SecurityGroup(
    resource_name='ha-proxy-sg',
    name='ha-proxy-sg',
    description='Security group for HAProxy Server',
    egress=[{
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": ["0.0.0.0/0"]
    }]
)

for description, port in HA_PROXY_PORTS.items():
    aws.vpc.SecurityGroupIngressRule(
        resource_name=f'allow-{description}',
        security_group_id=ha_proxy_sg.id,
        ip_protocol='tcp',
        cidr_ipv4='0.0.0.0/0',
        from_port=port,
        to_port=port
    )

ha_proxy_instance = aws.ec2.Instance(
    resource_name='ha-proxy',
    ami=common_infra.get_output('ami_id'),
    instance_type=aws.ec2.InstanceType.T3_MICRO,
    key_name=common_infra.get_output('key_pair')['key_name'],
    vpc_security_group_ids=[common_infra.get_output('ssh_access_sg_id'), ha_proxy_sg],
    availability_zone='eu-west-3a',
    tags={
        'Name': 'haproxy',
        'Role': 'haproxy'
    }
)

hosted_zone = aws.route53.get_zone(name='esuarez.info.')

for domain in SUBDOMAINS:
    aws.route53.Record(
        resource_name=f'{domain}-record',
        zone_id=hosted_zone.id,
        name=f'{domain}.esuarez.info',
        type=aws.route53.RecordType.A,
        ttl=300,
        records=[ha_proxy_instance.public_ip]
    )

pulumi.export('ha_proxy_public_ip', ha_proxy_instance.public_ip)
pulumi.export('ha_proxy_private_ip', ha_proxy_instance.private_ip)
