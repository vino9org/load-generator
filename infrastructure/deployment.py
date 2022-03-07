import os

import aws_cdk as cdk
from load_generator import load-generator

stack_name = os.environ.get("TESTING_STACK_NAME", "load-generator")
app = cdk.App()
load-generator(app, stack_name).build()
app.synth()
