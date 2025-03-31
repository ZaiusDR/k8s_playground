import pulumi

import pulumi_aws as aws

COMMON_TCP_PORTS = {'kubelet': 10250, 'kube-proxy': 10256, 'dns-tcp': 53, 'dns-tcp-flannel': 9153}
COMMON_UDP_PORTS = {'dns-udp': 53, 'flannel-vxlan': 8472}
CONTROL_PLANE_PORTS = {'kube-apiserver': 6443, 'etcd-client': 2379, 'etcd-peers': 2380}
TRAEFIK_PORTS = {'traefik-http': 30080, 'traefik-https': 30443}

EBS_OPTIONS = [{
    'device_name': '/dev/sda1',
    'delete_on_termination': True,
    'volume_size': 16
}]
IAM_INSTANCE_PROFILE = 'k8s-cluster-node'

common_infra_outputs = pulumi.StackReference('ZaiusDR/common_infra/live')
ha_proxy_outputs = pulumi.StackReference('ZaiusDR/ha_proxy/live')

ha_proxy_private_ip = ha_proxy_outputs.get_output('ha_proxy_private_ip')
ha_proxy_private_cidr = ha_proxy_private_ip.apply(lambda ip: f'{ip}/32')
vpc_cidr = common_infra_outputs.get_output('default_vpc')['cidr_block']

def add_rules_to_security_group(ports, security_group, cidr_block, prefix, protocol='tcp'):
    for key, port in ports.items():
        aws.vpc.SecurityGroupIngressRule(
            resource_name=f'allow-{prefix}-{key}',
            security_group_id=security_group.id,
            ip_protocol=protocol,
            cidr_ipv4=cidr_block,
            from_port=port,
            to_port=port,
        )

# Control Plane Nodes
control_plane_sg = aws.ec2.SecurityGroup(
    resource_name='control-plane-sg',
    name='control-plane-sg',
    description='Security group for Control Plane Nodes',
    egress=[{
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": ["0.0.0.0/0"]
    }]
)

add_rules_to_security_group(COMMON_TCP_PORTS, control_plane_sg, vpc_cidr, 'control-plane')
add_rules_to_security_group(CONTROL_PLANE_PORTS, control_plane_sg, vpc_cidr, 'control-plane')
add_rules_to_security_group(TRAEFIK_PORTS, control_plane_sg, ha_proxy_private_cidr, 'control-plane')
add_rules_to_security_group(COMMON_UDP_PORTS, control_plane_sg, vpc_cidr, 'control-plane', protocol='udp')

control_plane_instance = aws.ec2.Instance(
    resource_name='control-plane01',
    ami=common_infra_outputs.get_output('ami_id'),
    instance_type=aws.ec2.InstanceType.T3A_SMALL,
    key_name=common_infra_outputs.get_output('key_pair')['key_name'],
    vpc_security_group_ids=[common_infra_outputs.get_output('ssh_access_sg_id'), control_plane_sg.id],
    availability_zone='eu-west-3a',
    iam_instance_profile=IAM_INSTANCE_PROFILE,
    ebs_block_devices=EBS_OPTIONS,
    tags={
        'Name': 'control-plane01',
        'Cluster': 'k8s-cluster-node',
        'Role': 'control-plane'
    }
)

# Worker Nodes
nodes_sg = aws.ec2.SecurityGroup(
    resource_name='nodes-sg',
    name='nodes-sg',
    description='Security group for Worker Nodes',
    egress=[{
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": ["0.0.0.0/0"]
    }]
)

add_rules_to_security_group(COMMON_TCP_PORTS, nodes_sg, vpc_cidr, 'workers')
add_rules_to_security_group(TRAEFIK_PORTS, nodes_sg, ha_proxy_private_cidr, 'workers')
add_rules_to_security_group(COMMON_UDP_PORTS, nodes_sg, vpc_cidr, 'workers', protocol='udp')

aws.vpc.SecurityGroupIngressRule(
    resource_name='allow-nodeports',
    security_group_id=nodes_sg.id,
    ip_protocol='tcp',
    cidr_ipv4=ha_proxy_private_cidr,
    from_port=30000,
    to_port=32767,
)

for node in range(1, 4):
    aws.ec2.Instance(
        resource_name=f'control-node0{node}',
        ami=common_infra_outputs.get_output('ami_id'),
        instance_type=aws.ec2.InstanceType.T3A_MEDIUM,
        key_name=common_infra_outputs.get_output('key_pair')['key_name'],
        vpc_security_group_ids=[common_infra_outputs.get_output('ssh_access_sg_id'), control_plane_sg.id],
        availability_zone='eu-west-3a',
        iam_instance_profile=IAM_INSTANCE_PROFILE,
        ebs_block_devices=EBS_OPTIONS,
        tags={
            'Name': f'node0{node}',
            'Cluster': 'k8s-cluster-node',
            'Role': 'worker'
        }
    )

hosted_zone = aws.route53.get_zone(name='esuarez.info.', private_zone=True)

aws.route53.Record(
    resource_name=f'k8s-private-record',
    zone_id=hosted_zone.id,
    name='k8s.esuarez.info',
    type=aws.route53.RecordType.A,
    ttl=300,
    records=[ha_proxy_private_ip]
)
