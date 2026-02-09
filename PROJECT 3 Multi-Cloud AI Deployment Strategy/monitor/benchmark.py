import requests
import time
import pandas as pd
import concurrent.futures

# Endpoint URLs (Mocked for local test, would be real cloud URIs in production)
ENDPOINTS = {
    "AWS SageMaker": "http://localhost:8080/predict",
    "GCP Vertex AI": "http://localhost:8080/predict",
    "Azure AI Studio": "http://localhost:8080/predict"
}

def benchmark_endpoint(name, url, payload):
    start = time.perf_counter()
    try:
        response = requests.post(url, json=payload, timeout=10)
        latency = (time.perf_counter() - start) * 1000
        if response.status_code == 200:
            data = response.json()
            return {
                "Provider": name,
                "Status": "Success",
                "Total Latency (ms)": round(latency, 2),
                "Processing Time (ms)": data.get("processing_time_ms"),
                "Sentiment": data.get("sentiment"),
                "Confidence": data.get("confidence")
            }
        else:
            return {"Provider": name, "Status": f"Error {response.status_code}"}
    except Exception as e:
        return {"Provider": name, "Status": f"Failed: {str(e)}"}

def run_benchmarks(num_requests=5):
    test_payload = {"text": "This multi-cloud deployment strategy is project is excellent and amazing!"}
    all_results = []
    
    print(f"Starting benchmarks across {len(ENDPOINTS)} providers...")
    
    for _ in range(num_requests):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(benchmark_endpoint, name, url, test_payload) for name, url in ENDPOINTS.items()]
            for future in concurrent.futures.as_completed(futures):
                all_results.append(future.result())
                
    df = pd.DataFrame(all_results)
    return df

if __name__ == "__main__":
    results_df = run_benchmarks(num_requests=10)
    print("\nBenchmark Results Summary:")
    print(results_df.groupby("Provider")["Total Latency (ms)"].describe())
    results_df.to_csv("benchmark_results.csv", index=False)
    print("\nResults saved to benchmark_results.csv")
