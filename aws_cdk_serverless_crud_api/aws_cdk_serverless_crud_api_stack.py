from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam, RemovalPolicy
)
from constructs import Construct


class AwsCdkServerlessCrudApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB Table
        tasks_table = dynamodb.Table(
            self, "TasksTable",
            table_name="TasksTable",
            partition_key={"name": "taskId", "type": dynamodb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY
        )

        # Define Lambda Function Role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaDynamoDBExecutionRole")
            ]
        )

        # Lambda Functions
        create_task_lambda = _lambda.Function(
            self, "CreateTaskFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="create_task.handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            environment={
                "TASKS_TABLE_NAME": tasks_table.table_name
            },
            role=lambda_role
        )

        get_task_lambda = _lambda.Function(
            self, "GetTaskFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="get_task.handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            environment={
                "TASKS_TABLE_NAME": tasks_table.table_name
            },
            role=lambda_role
        )

        update_task_lambda = _lambda.Function(
            self, "UpdateTaskFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="update_task.handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            environment={
                "TASKS_TABLE_NAME": tasks_table.table_name
            },
            role=lambda_role
        )

        delete_task_lambda = _lambda.Function(
            self, "DeleteTaskFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="delete_task.handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            environment={
                "TASKS_TABLE_NAME": tasks_table.table_name
            },
            role=lambda_role
        )

        # API Gateway
        api = apigateway.RestApi(self, "TasksApi",
            rest_api_name="Tasks Service",
            description="This service serves tasks."
        )

        # Define API GATEWAY json schema for POST and PUT requests
        task_model = apigateway.Model(
            self, "TaskModel",
            rest_api=api,
            content_type="application/json",
            model_name="TaskModel",
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title="Task Model",
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    "title": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING),
                    "description": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING),
                    "status": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING)
                },
                required=["title", "description", "status"]
            )
        )

        tasks = api.root.add_resource("tasks")

        task = tasks.add_resource("{taskId}")

        tasks.add_method(
            "POST",
            apigateway.LambdaIntegration(create_task_lambda),
            request_models={
                "application/json": task_model
            })
        task.add_method("GET", apigateway.LambdaIntegration(get_task_lambda))
        task.add_method(
            "PUT",
            apigateway.LambdaIntegration(update_task_lambda),
            request_models={
                "application/json": task_model
            })
        task.add_method("DELETE", apigateway.LambdaIntegration(delete_task_lambda))

        # Lambda permissions to access DynamoDB
        tasks_table.grant_read_write_data(create_task_lambda)
        tasks_table.grant_read_data(get_task_lambda)
        tasks_table.grant_read_write_data(update_task_lambda)
        tasks_table.grant_read_write_data(delete_task_lambda)
