from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import os

def deploy_to_azure_ml(subscription_id, resource_group, workspace_name, model_name, endpoint_name):
    """
    Simulates or executes Azure Machine Learning deployment logic.
    """
    print(f"Connecting to Azure ML Workspace: {workspace_name}")
    ml_client = MLClient(DefaultAzureCredential(), subscription_id, resource_group, workspace_name)

    from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model, Environment
    
    print(f"Creating Managed Online Endpoint: {endpoint_name}")
    endpoint = ManagedOnlineEndpoint(name=endpoint_name)
    ml_client.online_endpoints.begin_create_or_update(endpoint).wait()

    print(f"Deploying Model: {model_name}")
    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name=endpoint_name,
        model=model_name,
        instance_type="Standard_DS2_v2",
        instance_count=1,
        environment_variables={'CLOUD_PROVIDER': 'Azure_AIStudio'}
    )
    ml_client.online_deployments.begin_create_or_update(deployment).wait()

    print("Deployment to Azure Machine Learning initiated successfully.")

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description='Deploy to Azure ML for a specific organization.')
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
    azure_config = org_config.get('azure', {})

    print(f"🚀 Deploying for Organization: {org_key} ({org_config.get('description')})")

    SUB_ID = azure_config.get('subscription_id') or os.getenv("AZURE_SUBSCRIPTION_ID", "your-subscription-id")
    RG = azure_config.get('resource_group') or os.getenv("AZURE_RESOURCE_GROUP", "your-resource-group")
    WORKSPACE = azure_config.get('workspace') or os.getenv("AZURE_WORKSPACE", "your-workspace")
    
    try:
        deploy_to_azure_ml(SUB_ID, RG, WORKSPACE, f"multi-cloud-azure-model-{org_key}", f"multi-cloud-endpoint-{org_key}")
    except Exception as e:
        print(f"Azure Deployment failed: {e}")
        print("Note: Ensure Azure CLI is logged in and credentials are set.")
