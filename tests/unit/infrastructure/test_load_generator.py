import os

import aws_cdk as cdk
import aws_cdk.assertions as assertions
import pytest
from aws_cdk.assertions import Template

from load_generator import load-generator


@pytest.fixture(scope="session")
def stack() -> Template:
    stack_name = os.environ.get("TESTING_STACK_NAME", "load-generator")
    app = cdk.App()
    stack = load-generator(app, "load-generator")
    return assertions.Template.from_stack(stack)

def test_stack_created(stack):
    assert stack
