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
        # Wait for the table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='TasksTable')

        # Add a sample item to the table
        table.put_item(Item={'taskId': '123', 'title': 'Old Title', 'description': 'Old Description', 'status': 'pending'})

        yield


def test_update_task_success(dynamodb_setup):
    from lambda_functions.update_task import handler

    # Sample event for the Lambda function
    event = {
        'pathParameters': {
            'taskId': '123'
        },
        'body': json.dumps({
            'title': 'New Title',
            'description': 'New Description',
            'status': 'completed'
        })
    }
    context = {}  # Mock context object

    # Call the Lambda function
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['title'] == 'New Title'
    assert body['description'] == 'New Description'
    assert body['status'] == 'completed'

    # Verify item has been updated
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('TasksTable')
    result = table.get_item(Key={'taskId': '123'})
    item = result.get('Item')
    assert item['title'] == 'New Title'
    assert item['description'] == 'New Description'
    assert item['status'] == 'completed'


def test_update_task_missing_task_id(dynamodb_setup):
    from lambda_functions.update_task import handler

    # Sample event for the Lambda function
    event = {
        'pathParameters': {},
        'body': json.dumps({
            'title': 'New Title',
            'description': 'New Description',
            'status': 'completed'
        })
    }
    context = {}  # Mock context object

    # Call the Lambda function
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'taskId is required in pathParameters'


def test_update_task_missing_body(dynamodb_setup):
    from lambda_functions.update_task import handler

    # Sample event for the Lambda function
    event = {
        'pathParameters': {
            'taskId': '123'
        }
    }
    context = {}  # Mock context object

    # Call the Lambda function
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Body is required'


def test_update_task_invalid_json(dynamodb_setup):
    from lambda_functions.update_task import handler

    # Sample event for the Lambda function
    event = {
        'pathParameters': {
            'taskId': '123'
        },
        'body': 'invalid-json'
    }
    context = {}  # Mock context object

    # Call the Lambda function
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Invalid JSON in request body'


def test_update_task_missing_field(dynamodb_setup):
    from lambda_functions.update_task import handler

    # Sample event for the Lambda function
    event = {
        'pathParameters': {
            'taskId': '123'
        },
        'body': json.dumps({
            'title': 'New Title',
            'description': 'New Description'
            # 'status' is missing
        })
    }
    context = {}  # Mock context object

    # Call the Lambda function
    response = handler(event, context)

    # Check response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'status is required in the body'
