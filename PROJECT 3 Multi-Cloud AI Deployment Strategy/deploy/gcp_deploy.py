from google.cloud import aiplatform
import os

def deploy_to_vertex_ai(project, location, display_name, container_uri):
    """
    Simulates or executes GCP Vertex AI deployment logic.
    """
    print(f"Initializing Vertex AI for project {project} in {location}")
    aiplatform.init(project=project, location=location)

    print(f"Uploading Model: {display_name}")
    model = aiplatform.Model.upload(
        display_name=display_name,
        serving_container_image_uri=container_uri,
        serving_container_environment_variables={'CLOUD_PROVIDER': 'GCP_VertexAI'}
    )

    print(f"Deploying to Endpoint...")
    endpoint = model.deploy(
        machine_type="n1-standard-4",
    )

    print(f"Deployment to GCP Vertex AI initiated successfully. Endpoint ID: {endpoint.resource_name}")

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description='Deploy to GCP Vertex AI for a specific organization.')
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
    gcp_config = org_config.get('gcp', {})

    print(f"🚀 Deploying for Organization: {org_key} ({org_config.get('description')})")

    PROJECT_ID = gcp_config.get('project_id') or os.getenv("GCP_PROJECT_ID", "your-project-id")
    REGION = gcp_config.get('region') or os.getenv("GCP_REGION", "us-central1")
    IMAGE = os.getenv("GCR_IMAGE_URI", "gcr.io/your-project/multi-cloud-ai:latest")
    
    try:
        deploy_to_vertex_ai(PROJECT_ID, REGION, f"multi-cloud-vertex-model-{org_key}", IMAGE)
    except Exception as e:
        print(f"GCP Deployment failed: {e}")
        print("Note: Ensure GCP SDK is authenticated and project settings are correct.")
