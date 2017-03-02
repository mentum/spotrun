from marshmallow import Schema, fields


class AWSConfig(Schema):
    region = fields.Str(required=True)

    # While it is possible to start
    # a timed instance without bidding in the AWS Console,
    # it doesn't seem to be possible via boto, so we need
    # to specify a bid in the config
    bid = fields.Str(required=True)

    max_lifetime = fields.Int(default=6)


class ConfigSchema(Schema):
    name = fields.Str(required=True)

    command = fields.Str(required=True)
    stdout = fields.Str(required=True)
    stderr = fields.Str(required=True)

    input_files = fields.Dict(required=True)
    aws_config = fields.Nested(AWSConfig, required=True)
    private_key_path = fields.Str(required=True)
    instance_spec = fields.Dict(required=True)
