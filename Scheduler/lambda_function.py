import json
import boto3
from boto3.dynamodb.conditions import Key
import random

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
    
def lambda_handler(event, context):
    
    function_name = event.get('function_name')
    function_params = event.get('params', {})
    bucket_rr = 'roundrobin-bucket'
    bucket_region = 'carbon-state-bucket'
    rr_file = 'round_robin_state.json'
    region_file = 'best_regions.json'


    if not function_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Function name is required'})
        }

    table_name = 'LambdaProfilingData'
    table = dynamodb.Table(table_name)

    try:
        response = table.query(
            KeyConditionExpression=Key('function_name').eq(function_name)
        )
        
        if 'Items' in response and len(response['Items']) > 0:
            item = response['Items'][0]

            time = float(item.get('execution_time', 0))
            memory = float(item.get('memory_used', 0))
            max_input = int(item.get('max_input', 0))
            min_input = int(item.get('min_input', 0))

            if(time < 100 and memory < 100):
                intensity = calculate_intensity(function_name, function_params, time, memory, max_input, min_input)
            else:
                intensity = 'high' 

            json_rr = read_json_from_s3(bucket_rr, rr_file)
            round_robin_list = json_rr['round_robin']
            index = get_index(intensity, round_robin_list)
            
            json_region = read_json_from_s3(bucket_region, region_file)
            best_regions_list = json_region['best_regions']
            region = get_region(intensity, index, best_regions_list)
            
            new_index = (index%3) + 1
            
            update_index(json_rr, intensity, new_index, bucket_rr, rr_file)
            
            response_payload = invoke_lambda(function_name,function_params,region.lower())
            response = json.loads(response_payload)
            body = response.get('body', '{}')
            
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'function_name': function_name,
                    'region': region,
                    'response' : json.loads(body)
                })
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Item not found'})
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error reading item', 'error': str(e)})
        }



def calculate_intensity(function_name, function_params, time, memory, max_input, min_input):
    function = {
        'Fibonacci': extract_fibonacci,
        'InverseMatrix': extract_inverseMatrix,
        'LinearRegression': extract_linearRegression
    }
            
    extraction_function = function.get(function_name)
    if extraction_function:
        input = extraction_function(function_params)
    else:
        raise ValueError(f"Invalid command: {function_name}")
        
    normalized_input = normalize(input, min_input, max_input)
    normalized_time = normalize(time, 1, 100)
    normalized_memory = normalize(memory, 1, 100)

    metric = 0.4*normalized_input+0.3*normalized_time+0.3*normalized_memory

    if(metric >= 0.5):
        return 'high'
    else:
        return 'low'

        
def normalize(value, min_value, max_value):
    if min_value == max_value:
        raise ValueError("The min value and the max value must be different")
    return (value - min_value) / (max_value - min_value)
    
def extract_fibonacci(function_params):
    n = function_params.get('n', None)
    return n
    
def extract_inverseMatrix(function_params):
    matrix = function_params.get('matrix', [])
    dimension = len(matrix)
    return dimension
        
def extract_linearRegression(function_params):
    data = function_params.get('data', '{}')
    X = data.get('X', [])
    return len(X[0])
    

def read_json_from_s3(bucket_name, file_key):
    s3_response_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = s3_response_object['Body'].read().decode('utf-8')
    # Load the JSON in a Python dictionary
    json_content = json.loads(file_content)
    return json_content
    
    
def get_index(intensity, round_robin):
    for entry in round_robin:
        if intensity == entry['group']:
            return entry['index']
    return None
        
        
def get_region(intensity, index, best_regions):
    for entry in best_regions:
        if intensity == entry['group'] and index == entry['index']:
            return entry['region']
    return None
    
def update_index(data, intensity, new_index, bucket_name, file_key):
    for item in data.get('round_robin', []):
        if item['group'] == intensity:
            item['index'] = new_index
        
    updated_content = json.dumps(data, indent=4)
        
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=updated_content, ContentType='application/json')
        

def invoke_lambda(function_name, function_params, region):
    if(region == 'us-east-1' or region == 'us-west-2'):
        lambda_client = boto3.client('lambda', region_name=region)
    else:
        n = random.randint(1, 2)
        if(n == 1):
            lambda_client = boto3.client('lambda', region_name='us-east-1')
        else:
            lambda_client = boto3.client('lambda', region_name='us-west-2')
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',  # 'Event' per invocazioni asincrone
        Payload=json.dumps(function_params)
    )
    
    response_payload = response['Payload'].read().decode('utf-8')
    return response_payload