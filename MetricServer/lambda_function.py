import json
import boto3
import requests

def lambda_handler(event, context):
    
    #Electricity Maps
    api_key = 'qkJvWx0M8k5my'
    base_url = 'https://api.electricitymap.org/v3/carbon-intensity/latest'
    base_url2 = 'https://api.electricitymap.org/v3/power-breakdown/latest'
    
    # List of AWS regions mapped on Electricity Map zones
    aws_regions = {
        "US-EAST-1":{
            "zone": "US-MIDA-PJM"
        },
        "US-EAST-2":{
            "zone": "US-MIDA-PJM"
        },
        "US-WEST-1":{
            "zone": "US-CAL-CISO"
        },
        "US-WEST-2":{
            "zone": "US-NW-PACW"
        },
        "AF-SOUTH-1":{
            "zone": "ZA"
        },
        "AP-SOUTH-1":{
            "zone": "IN-WE"
        },
        "AP-SOUTH-2":{
            "zone": "IN-SO"
        },
        "AP-SOUTHEAST-1":{
            "zone": "SG"
        },
        "AP-SOUTHEAST-2":{
            "zone": "AU-NSW"
        },
        "AP-SOUTHEAST-3":{
            "zone": "ID"
        },
        "AP-SOUTHEAST-4":{
            "zone": "AU-VIC"
        },
        "AP-NORTHEAST-1":{
            "zone": "JP-TK"
        },
        "AP-NORTHEAST-2":{
            "zone": "KR"
        },
        "AP-NORTHEAST-3":{
            "zone": "JP-KN"
        },
        "CA-CENTRAL-1":{
            "zone": "CA-AB"
        },
        "EU-CENTRAL-1":{
            "zone": "DE"
        },
        "EU-CENTRAL-2":{
            "zone": "CH"
        },
        "EU-WEST-1":{
            "zone": "IE"
        },
        "EU-WEST-2":{
            "zone": "GB"
        },
        "EU-WEST-3":{
            "zone": "FR"
        },
        "EU-NORTH-1":{
            "zone": "SE-SE3"
        },
        "EU-SOUTH-1":{
            "zone": "IT-NO"
        },
        "EU-SOUTH-2":{
            "zone": "ES"
        },
        "ME-SOUTH-1":{
            "zone": "BH"
        },
        "ME-CENTRAL-1":{
            "zone": "AE"
        },
        "SA-EAST-1":{
            "zone": "BR-CS"
        },
        "CA-WEST-1":{
            "zone": "CA-AB"
        },
        "IL-CENTRAL-1":{
            "zone": "IL"
        }
    }

    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    # Dictionary to store the carbon data and energy data for all regions
    carbon_data = {}
    energy_type = {}
    
    # Iterate over each AWS region
    for region, details in aws_regions.items():
        # Make a GET request to the Electricity Maps API for the current region
        response = requests.get(f"{base_url}?zone={details['zone']}", headers=headers)
        response2 = requests.get(f"{base_url2}?zone={details['zone']}", headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            carbon_data[region] = data
        else:
            carbon_data[region] = {
                'error': response.text
            }
            
        # Check if the request2 was successful
        if response2.status_code == 200:
            data2 = response2.json()
            energy_type[region] = data2
        else:
             energy_type[region] = {
                'error': response2.text
            }

        # Upload the JSON data to S3
        s3 = boto3.client('s3')
        bucket_name = 'apicarbon-bucket'
        file_name = 'carbon_data.json'
        file_name2 = 'energy_type.json'
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(carbon_data)
        )
        
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name2,
            Body=json.dumps(energy_type)
        )
    
    return {
        'statusCode': 200,
        'body': "Success"
    }

