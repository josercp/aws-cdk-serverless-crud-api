import json
import os
import pytest
from moto import mock_aws
import boto3


@pytest.fixture(scope='module')
def setup_dynamodb():
    """Sets up a mocked DynamoDB for testing and sets environment variables."""
    os.environ['TASKS_TABLE_NAME'] = 'TasksTable'

    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        # Create a DynamoDB table only if it does not exist
        existing_tables = dynamodb.meta.client.list_tables().get('TableNames', [])
        if 'TasksTable' not in existing_tables:
            dynamodb.create_table(
                TableName=os.environ['TASKS_TABLE_NAME'],
                KeySchema=[
                    {'AttributeName': 'taskId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'taskId', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
        table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])
        table.meta.client.get_waiter('table_exists').wait(TableName=os.environ['TASKS_TABLE_NAME'])
        yield


@pytest.fixture
def mock_event():
    """Returns a mock event for testing."""
    return {
        'body': json.dumps({
            'title': 'Test Task',
            'description': 'This is a test task',
            'status': 'pending'
        })
    }


@mock_aws
def test_create_task_invalid_body(setup_dynamodb):
    """Tests the case where the request body is invalid."""
    from lambda_functions.create_task import handler  # Import inside the test
    invalid_event = {
        'body': json.dumps({
            'title': 'Invalid Task'
            # Missing 'description' and 'status'
        })
    }
    response = handler(invalid_event, None)

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


@mock_aws
def test_create_task_success(setup_dynamodb, mock_event):
    """Tests the successful case of the handler function."""
    from lambda_functions.create_task import handler  # Import inside the test
    response = handler(mock_event, None)

    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'taskId' in body
    assert body['title'] == 'Test Task'
    assert body['description'] == 'This is a test task'
    assert body['status'] == 'pending'

    # Verify the task is stored in DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])
    result = table.get_item(Key={'taskId': body['taskId']})

    assert 'Item' in result
    item = result['Item']
    assert item['title'] == 'Test Task'
    assert item['description'] == 'This is a test task'
    assert item['status'] == 'pending'


if __name__ == "__main__":
    pytest.main()
