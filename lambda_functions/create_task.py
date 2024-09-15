import json
import uuid
import os
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger


# Setting Powertools logger
logger = Logger(service="create-task")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASKS_TABLE_NAME'])


def handler(event, context):
    try:
        body = json.loads(event['body'])

        # Generate new ID
        task_id = str(uuid.uuid4())

        # Trying save item into DynamoDB
        try:
            table.put_item(
                Item={
                    'taskId': task_id,
                    'title': body['title'],
                    'description': body['description'],
                    'status': body['status']
                }
            )
        except ClientError as e:
            logger.error(f'Error saving task: {e.response["Error"]["Message"]}')
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Error saving task: {e.response["Error"]["Message"]}'})
            }

        # Success
        logger.info(f'Task created with ID: {task_id}')
        return {
            'statusCode': 201,
            'body': json.dumps({
                'taskId': task_id,
                'title': body['title'],
                'description': body['description'],
                'status': body['status']
            })
        }

    except Exception as e:
        logger.error(f'Internal server error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
