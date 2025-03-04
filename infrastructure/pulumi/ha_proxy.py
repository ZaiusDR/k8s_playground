import pulumi

import pulumi_aws as aws

from common_infra import ssh_sg

HA_PROXY_PORTS = {'http': 80, 'https': 443, 'k8s-api': 6443}

ubuntu_ami_id_ssm_path = '/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id'
ami_id = aws.ssm.get_parameter(name=ubuntu_ami_id_ssm_path)
key_pair = aws.ec2.get_key_pair(key_name='k8s-cluster-key-pair')

ha_proxy_sg = aws.ec2.SecurityGroup('ha-proxy-sg',
    name='ha-proxy-sg',
    description='Security group for HAProxy Server'
)

for description, port in HA_PROXY_PORTS.items():
    aws.vpc.SecurityGroupIngressRule(f'allow-{description}',
        security_group_id=ha_proxy_sg.id,
        ip_protocol='tcp',
        cidr_ipv4='0.0.0.0/0',
        from_port=port,
        to_port=port)

ha_proxy = aws.ec2.Instance('ha-proxy',
    ami=ami_id.value,
    instance_type=aws.ec2.InstanceType.T3_MICRO,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[ssh_sg.id, ha_proxy_sg],
    tags={
        'Name': 'haproxy',
        'Role': 'haproxy'
    })

pulumi.export('ha_proxy_public_ip', ha_proxy.public_ip)
pulumi.export('ha_proxy_private_ip', ha_proxy.private_ip)
