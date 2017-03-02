from spotrun import logger

import boto3

import ntpath

import os

import paramiko

import time

USERNAME = "ubuntu"  # TODO: Support AMIs that are not ubuntu-based
WORKSPACE_NAME = "spotrun"


class SpotrunInstance(object):

    def __init__(self, key_path, instance_spec, region, bid, max_lifetime):

        self.spec = instance_spec
        self.region = region
        self.bid = bid
        self.max_lifetime = max_lifetime

        self._instance = self._create()

        # Once the instance is initialized, set up SSH & SFTP
        self.ssh = self._configure_ssh(key_path)
        self.sftp = self._configure_sftp(key_path)

        # Initialize workspace
        logger.info('Initializing workspace...')
        self.sftp.mkdir(WORKSPACE_NAME)
        self.sftp.chdir(WORKSPACE_NAME)

    @property
    def id(self):
        return self._instance.id

    @property
    def public_dns_name(self):
        return self._instance.public_dns_name

    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def _configure_ssh(self, key_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        did_connect = False
        logger.info("Waiting for SSH Access...")
        while not did_connect:
            try:
                ssh.connect(self.public_dns_name, username=USERNAME, key_filename=key_path)
                did_connect = True
                logger.info("Connected.")
                return ssh
            except:
                # TODO: Count retries and raise.
                # Not doing it right now because SSH init times vary from
                # one AMI to the other.
                pass

    def _configure_sftp(self, key_path):
        try_count = 0
        sftp = None
        key = paramiko.RSAKey.from_private_key_file(key_path)
        logger.info("Attempting SFTP connection...")
        while try_count < 5:
            try:
                transport = paramiko.Transport((self.public_dns_name, 22))
                transport.connect(username=USERNAME, pkey=key)
                sftp = paramiko.SFTPClient.from_transport(transport)
                logger.info("SFTP Connected.")
                return sftp
            except paramiko.ssh_exception.SSHException:
                try_count += 1
                if try_count == 5:
                    raise

    def _create(self):
        logger.info("Creating EC2 client...")
        ec2 = boto3.resource('ec2', region_name=self.region)
        client = boto3.client('ec2', region_name=self.region)

        logger.info("Instance Creation")
        logger.info("-----------------")
        logger.info('AMI: {}'.format(self.spec.get('ImageId')))
        logger.info('Instance: {}'.format(self.spec.get('InstanceType')))
        logger.info('Keypair: {}'.format(self.spec.get('KeyName')))
        logger.info('Max Lifetime: {} hours'.format(self.max_lifetime))

        if self.max_lifetime > 6:
            raise ValueError("Max lifetime of the instance cannot be larger than 6 hours")

        response = client.request_spot_instances(
            SpotPrice=self.bid,
            BlockDurationMinutes=self.max_lifetime * 60,
            LaunchSpecification=self.spec
        )

        instance_id = None
        # Wait until spot request is fulfilled
        logger.info('Waiting for spot request fulfillment...')
        while instance_id is None:
            requests = response['SpotInstanceRequests']

            if len(requests) != 1:
                raise RuntimeError("Unexpected number of spot instance requests: {}".format(len(requests)))

            request = requests[0]

            if request['State'] == 'failed':
                # TODO: Rollback instance creation
                raise RuntimeError('Spot request "{}" failed'.format(request['SpotInstanceRequestId']))

            instance_id = request.get('InstanceId')

            if instance_id is None:
                response = client.describe_spot_instance_requests(SpotInstanceRequestIds=[request['SpotInstanceRequestId']])
                time.sleep(2)

        logger.info('Request fulfilled. Instance ID is "{}".'.format(instance_id))

        # Create instance object and wait for it to be ready
        instance = ec2.Instance(instance_id)

        logger.info('Waiting for instance "{}" to be ready...'.format(instance_id))

        instance.wait_until_running()

        logger.info("Instance ready.")

        return instance

    def upload_file(self, local_path, instance_path):
        filename = SpotrunInstance.path_leaf(local_path)
        dest = os.path.join(instance_path, filename)
        logger.info("Uploading {}...".format(local_path))
        self.sftp.put(local_path, dest)

    def upload_dir(self, folder_path, instance_path):
        for dirpath, dirnames, filenames in os.walk(folder_path):
            dest = os.path.join(instance_path, dirpath)
            self.sftp.mkdir(dest)

            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                self.upload_file(local_path, dest)

    def execute_commands(self, commands):
        stdin, stdout, ssh_stderr = self.ssh.exec_command(';'.join(commands))
        out = stdout.read()
        err = ssh_stderr.read()

        stdin.flush()

        return out, err
