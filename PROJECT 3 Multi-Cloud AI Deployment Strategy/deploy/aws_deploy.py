import boto3
import os

def deploy_to_sagemaker(image_uri, role_arn, model_name, endpoint_config_name, endpoint_name):
    """
    Simulates or executes AWS SageMaker deployment logic.
    """
    sagemaker = boto3.client('sagemaker', region_name='us-east-1')
    
    print(f"Creating SageMaker Model: {model_name}")
    try:
        sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer={'Image': image_uri, 'Environment': {'CLOUD_PROVIDER': 'AWS_SageMaker'}},
            ExecutionRoleArn=role_arn
        )
    except sagemaker.exceptions.ClientError as e:
        if "AlreadyExists" in str(e):
            print(f"Model {model_name} already exists, skipping creation.")
        else: raise e
    
    print(f"Creating Endpoint Config: {endpoint_config_name}")
    try:
        sagemaker.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[{
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.t2.medium',
            }]
        )
    except sagemaker.exceptions.ClientError as e:
        if "AlreadyExists" in str(e):
            print(f"Endpoint config {endpoint_config_name} already exists, skipping creation.")
        else: raise e
    
    print(f"Creating Endpoint: {endpoint_name}")
    try:
        sagemaker.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
    except sagemaker.exceptions.ClientError as e:
        if "AlreadyExists" in str(e):
            print(f"Endpoint {endpoint_name} already exists, skipping creation.")
        else: raise e
    
    print("Deployment to AWS SageMaker initiated successfully.")

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description='Deploy to AWS SageMaker for a specific organization.')
    parser.add_argument('--org', type=str, help='Organization key from config/org_config.json')
    args = parser.parse_args()

    # Load Config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'org_config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    # Determine Org
    org_key = args.org if args.org else config.get('default')
    if org_key not in config['organizations']:
        print(f"Error: Organization '{org_key}' not found in config.")
        print(f"Available organizations: {list(config['organizations'].keys())}")
        sys.exit(1)
    
    org_config = config['organizations'][org_key]
    aws_config = org_config.get('aws', {})

    print(f"🚀 Deploying for Organization: {org_key} ({org_config.get('description')})")
    
    # Parameters
    DEPLOY_IMAGE = os.getenv("ECR_IMAGE_URI", "123456789012.dkr.ecr.us-east-1.amazonaws.com/multi-cloud-ai:latest")
    ROLE = aws_config.get('role_arn') or os.getenv("SAGEMAKER_ROLE", "arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole")
    
    # Check for credentials before attempting execution
    try:
        deploy_to_sagemaker(DEPLOY_IMAGE, ROLE, f"multi-cloud-model-{org_key}", f"multi-cloud-config-{org_key}", f"multi-cloud-endpoint-{org_key}")
    except Exception as e:
        print(f"AWS Deployment failed: {e}")
        print("Note: Ensure AWS credentials and ECR image are properly configured.")
