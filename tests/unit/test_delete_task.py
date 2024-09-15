import json
import os
import pytest
from moto import mock_aws
import boto3


# Set environment variable
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
        table.put_item(Item={'taskId': '123', 'description': 'Test task'})

        yield


def test_delete_task_success(dynamodb_setup):
    from lambda_functions.delete_task import handler

    event = {
        'pathParameters': {
            'taskId': '123'
        }
    }
    context = {}
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 204
    assert response['body'] == ''

    # Verify item has been deleted
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('TasksTable')
    result = table.get_item(Key={'taskId': '123'})
    assert 'Item' not in result


def test_delete_task_not_found(dynamodb_setup):
    from lambda_functions.delete_task import handler

    event = {
        'pathParameters': {
            'taskId': 'non-existent-id'
        }
    }
    context = {}

    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 204
    assert response['body'] == ''

    # Verify nothing has changed
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('TasksTable')
    result = table.scan()
    assert len(result['Items']) == 1


def test_delete_task_error(dynamodb_setup):
    from lambda_functions.delete_task import handler

    event = {
        'pathParameters': {
            'taskId': '123'
        }
    }
    context = {}

    # Simulate a DynamoDB error
    with mock_aws():
        # Simulate table deletion before calling handler
        dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
        dynamodb_client.delete_table(TableName='TasksTable')

        response = handler(event, context)

        # Check response
        assert response['statusCode'] == 500
        assert 'error' in json.loads(response['body'])
