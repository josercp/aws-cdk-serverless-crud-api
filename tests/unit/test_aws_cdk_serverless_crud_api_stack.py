import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cdk_serverless_crud_api.aws_cdk_serverless_crud_api_stack import AwsCdkServerlessCrudApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_serverless_crud_api/aws_cdk_serverless_crud_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCdkServerlessCrudApiStack(app, "aws-cdk-serverless-crud-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
