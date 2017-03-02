from spotrun import logger
from spotrun.instance import SpotrunInstance

import os


class Task(object):

    def __init__(self, task_config):
        self._instance_spec = task_config['instance_spec']
        self._aws_config = task_config['aws_config']
        self._key = task_config['private_key_path']

        self.input_files = task_config['input_files']
        self.command = task_config['command']

        self.stdout_path = task_config['stdout']
        self.stderr_path = task_config['stderr']

        self.instance = None

    def setup(self):
        # Setup instance & upload files
        logger.info("Setting up instance...")
        self.instance = SpotrunInstance(self._key, self._instance_spec, **self._aws_config)

        for localpath, remotepath in self.input_files.items():

            if os.path.isfile(localpath):
                self.instance.upload_file(localpath, remotepath)

            elif os.path.isdir(localpath):
                self.instance.upload_dir(localpath, remotepath)

    def execute(self):
        logger.info('Executing the task...')
        # Execute the task
        cmds = [
            "cd spotrun",
            self.command
        ]

        stdout, stderr = self.instance.execute_commands(cmds)

        if stdout:
            with open(self.stdout_path, 'wb') as outfile:
                outfile.write(stdout)

        if stderr:
            with open(self.stderr_path, 'wb') as outfile:
                outfile.write(stderr)

    def teardown(self):
        logger.info('Downloading task output and tearing down...')

        # TODO: Download output files specified in task manifest
        # Destroy the instance
        self.instance.execute_commands(['sudo shutdown -h now'])
