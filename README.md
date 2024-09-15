
# Serverless Tasks API

This project is a serverless CRUD API for managing tasks using AWS CDK, Lambda, API Gateway, and DynamoDB. The API provides endpoints to create, read, update, and delete tasks. Each task contains attributes like `taskId`, `title`, `description`, and `status`.

Aquí tienes una versión actualizada de tu sección de **Prerequisites**, incluyendo cómo configurar las credenciales de AWS en AWS CLI:

## Prerequisites

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
- [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) installed
- Python 3.10 or above
- Node.js (for CDK)
- `pip` and `npm` package managers

### Configuring AWS CLI Credentials

1. Install the AWS CLI by following the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).
2. Run the following command to configure your AWS credentials:
   ```bash
   aws configure
   ```
3. You will be prompted to enter:
   - **AWS Access Key ID**: Your AWS Access Key ID.
   - **AWS Secret Access Key**: Your AWS Secret Access Key.
   - **Default region name**: The default AWS region, e.g., `us-east-1`.
   - **Default output format**: Choose `json`, `text`, or `table` (usually `json`).

   You can find your Access Key and Secret Key in the [AWS IAM Console](https://console.aws.amazon.com/iam/home).
4. To verify that your credentials are set up correctly, run:
   ```bash
   aws sts get-caller-identity
   ```
   This command should return information about your AWS account.

## Project Structure
```markdown
aws-cdk-serverless-crud-api/
├── cdk.json                                    # CDK project config
├── lambda_functions/                           # Directory containing Lambda functions
│   ├── create_task.py                          # Lambda to create a task
│   ├── get_task.py                             # Lambda to get a task by ID
│   ├── update_task.py                          # Lambda to update a task
│   └── delete_task.py                          # Lambda to delete a task by ID
├── test/                                       # Directory containing all tests
│   └── unit                                    # Directory containing Unit tests
│       ├── test_create_task.py                 # Test Lambda function create_task.py
│       ├── test_get_task.py                    # Test Lambda function get_task.py
│       ├── test_update_task.py                 # Test Lambda function update_task.py
│       └── test_delete_task.py                 # Test Lambda function delete_task.py
├── requirements.txt                            # Python dependencies for CDK
├── aws_cdk_serverless_crud_api/                # Directory containing CDK stack
│   └── aws_cdk_serverless_crud_api_stack.py    # CDK stack defining API Gateway, Lambda, and DynamoDB resources
└── README.md                                   # Documentation
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/josercp/aws-cdk-serverless-crud-api.git
cd aws-cdk-serverless-crud-api
```

### 2. Install Dependencies

You need to install both Python dependencies and AWS CDK:

```bash
pip install -r requirements.txt
npm install -g aws-cdk
```

### 3. Bootstrap Your Environment

If you haven't used CDK in your AWS environment before, you need to bootstrap it:

```bash
cdk bootstrap
```

### 4. Deploy the Stack

To deploy the stack, use the following command:

```bash
cdk deploy
```

The command will output the API Gateway endpoint that you can use to interact with the API.

## API Endpoints

### 1. Create Task (POST /tasks)

**Request:**

```json
POST /tasks
Content-Type: application/json
{
  "title": "Task 1",
  "description": "This is task 1",
  "status": "pending"
}
```

**Response:**

```json
{
  "taskId": "generated-unique-id",
  "title": "Task 1",
  "description": "This is task 1",
  "status": "pending"
}
```

### 2. Get Task (GET /tasks/{taskId})

**Response:**

```json
{
  "taskId": "123",
  "title": "Task 1",
  "description": "This is task 1",
  "status": "in-progress"
}
```

### 3. Update Task (PUT /tasks/{taskId})

**Request:**

```json
PUT /tasks/{taskId}
Content-Type: application/json
{
  "title": "Updated Task 1",
  "description": "This task has been updated",
  "status": "completed"
}
```
**Response:**

```json
{
  "title": "Updated Task 1",
  "description": "This task has been updated",
  "status": "completed"
}
```

### 4. Delete Task (DELETE /tasks/{taskId})

**Response:**

```http
204 No Content
```

## Testing the API

You can use tools like [curl](https://curl.se/) or [Postman](https://www.postman.com/) to test the API.

### Example: Using `curl`

- **Create Task:**
  ```bash
  curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Task 1", "description": "This is task 1", "status": "pending"}'
  ```

- **Get Task:**
  ```bash
  curl https://<api-id>.execute-api.<region>.amazonaws.com/prod/tasks/<taskId>
  ```

- **Update Task:**
  ```bash
  curl -X PUT https://<api-id>.execute-api.<region>.amazonaws.com/prod/tasks/<taskId> \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task 1", "description": "This task has been updated", "status": "completed"}'
  ```

- **Delete Task:**
  ```bash
  curl -X DELETE https://<api-id>.execute-api.<region>.amazonaws.com/prod/tasks/<taskId>
  ```

## Clean Up

To destroy the stack and prevent ongoing AWS costs, run:

```bash
cdk destroy
```

## Further Reading

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [DynamoDB Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- [AWS Lambda Functions](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [API Gateway REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)

## License

This project is licensed under the MIT License.