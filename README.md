# spotrun

`spotrun` is a tool for running one-off tasks in the cloud, via EC2 [spot instances](https://aws.amazon.com/ec2/spot/).



### Installation

```shell
$ pip install -r requirements.txt
$ python setup.py install
```



### Usage

```shell
$ spotrun {task_definition_file}
```



### Task Definition File

Here is an example task definition file (all fields are mandatory for now): 

```json
{
    "name": "TestTask",

    "command": "ls -al",

    "stdout": "out.txt",
    "stderr": "err.txt",

    "input_files": {
        "spotrun/": ".",
        "requirements.txt": "."
    },


    "aws_config": {
        "region": "us-east-1",
        "bid": "0.30",
        "max_lifetime": 5
    },

    "instance_spec": {
        "ImageId": "ami-b4b047a2",
        "KeyName": "dalloriam_mbp",
        "SecurityGroups": [
            "test_task"
        ],
        "InstanceType": "c3.large"
    },

    "private_key_path": "/Users/me/Desktop/mykey.pem"
}

```

#### File structure

* **name** : Name of the task
* **command**: Shell command to be executed on the instance
* **stdout**: The file in which to write the standard output stream of the command
* **stderr**: The file in which to write the standard error stream of the command
* **input_files**: Dictionary ( `{local_path: remote_folder}` ) listing the files to upload to the instance
* **aws_config**
  * **bid**: Maximum hourly price for the instance
  * **region**: Region of the instance
  * **max_lifetime**: Maximum lifetime of the instance (capped at 6 hours)
* **instance_spec**: AWS Instance parameters. Same format as the `LaunchSpecification` field from this `boto3` [method](http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.request_spot_instances).
* **private_key_path**: Private key used by spotrun to login to the instance. (Should be the private key corresponding to the `KeyName` keypair defined in AWS)



### TODO

* Support AMIs that are not ubuntu-based
* Rollback instance creation in the event of a failure
* Add support for downloading files from the instance after running the task