import json
import os
import pytest
from moto import mock_aws
import boto3


# Set environment variable for the table name
@pytest.fixture(scope='module', autouse=True)
def set_env_variable():
    os.environ['TASKS_TABLE_NAME'] = 'TasksTable'


@pytest.fixture
def dynamodb_setup():
    # Setup mock DynamoDB
    with mock_aws():
        # Create DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='TasksTable',
            KeySchema=[
                {
                    'AttributeName': 'taskId',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'taskId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='TasksTable')
        table.put_item(Item={'taskId': '123', 'title': 'Sample Task', 'description': 'Sample Description', 'status': 'pending'})

        yield


def test_get_task_success(dynamodb_setup):
    from lambda_functions.get_task import handler

    event = {
        'pathParameters': {
            'taskId': '123'
        }
    }
    context = {}
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['taskId'] == '123'
    assert body['title'] == 'Sample Task'
    assert body['description'] == 'Sample Description'
    assert body['status'] == 'pending'


def test_get_task_not_found(dynamodb_setup):
    from lambda_functions.get_task import handler

    event = {
        'pathParameters': {
            'taskId': '999'  # ID that does not exist
        }
    }
    context = {}

    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['message'] == 'Task not found'


def test_get_task_missing_task_id(dynamodb_setup):
    from lambda_functions.get_task import handler

    event = {
        'pathParameters': {}
    }
    context = {}
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'taskId is required in pathParameters'
