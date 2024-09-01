import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_api_name = 'apicarbon-bucket'
    bucket_state_name = 'carbon-state-bucket'
    carbon_file = 'carbon_data.json'
    energy_file = 'energy_type.json'
    regions_file = 'best_regions.json'

    try:
        json_carbon = read_json_from_s3(bucket_api_name, carbon_file)
        json_energy = read_json_from_s3(bucket_api_name, energy_file)
        
        #Create dictionary to store the results of the metric
        metric_results = []

        for region, data in json_carbon.items():
            intensity_carbon = data.get('carbonIntensity', 0)
            if region in json_energy:
                renewable_percentage = json_energy[region].get('renewablePercentage', {})
                metric = calculate_metric(intensity_carbon, renewable_percentage)
                metric_results.append((region, metric, intensity_carbon, renewable_percentage))
         
        #Get min and max value of the metric   
        min_metric = min(metric_results, key=lambda x: x[1])[1]
        max_metric = max(metric_results, key=lambda x: x[1])[1]
        
        best_regions = sorted(metric_results, key=lambda x: x[1], reverse=True)[:6]
        
        normalized_results = [
            (region, normalize_metric(metric, min_metric, max_metric), ic, rp)
            for region, metric, ic, rp in best_regions
        ]
        
        results = {
            "best_regions": [
                {"region": region, "EEI": metric, "carbonIntensity": ic, "renewablePercentage": rp, "group": 'high', "index": idx + 1}
                for idx, (region, metric, ic, rp) in enumerate(normalized_results[:3])
            ] + [
                {"region": region, "EEI": metric, "carbonIntensity": ic, "renewablePercentage": rp, "group": 'low', "index": idx + 1}
                for idx, (region, metric, ic, rp) in enumerate(normalized_results[3:])
            ]
        }
      
        update_regions(results, bucket_state_name, regions_file)
            
        return {
            'statusCode': 200,
            'body': "Success"
        }
    except Exception as e:
        print(f"Errore: {e}")
        return {
            'statusCode': 500,
            'body': str(e)
        }


#Function to read the carbon data stored on S3
def read_json_from_s3(bucket_name, file_key):
    s3_response_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = s3_response_object['Body'].read().decode('utf-8')
    # Load the JSON in a Python dictionary
    json_content = json.loads(file_content)
    return json_content
    

#Function to update the state of the lambda function with the current three best regions
def update_regions(regions, bucket_name, file_key):
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=json.dumps(regions))
    

def calculate_metric(intensity_carbon, renewable_percentage):
    return (1 / intensity_carbon) * (renewable_percentage / 100) if intensity_carbon != 0 else 0

def normalize_metric(value, min_value, max_value):
    if max_value == min_value:
        return 0  
    return ((value - min_value) / (max_value - min_value)) * 100

