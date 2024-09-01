import boto3
from PIL import Image
import io
import json

def lambda_handler(event, context):
    source_bucket = 'imgsource-bucket'
    destination_bucket = 'imgdestination-bucket'
    
    s3_client = boto3.client('s3')

    max_size = 500 
    
    for record in event['Records']:
        source_key = record['s3']['object']['key']
        
        try:
            response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
            image_data = response['Body'].read()
            image = Image.open(io.BytesIO(image_data))
            
            width, height = image.size
            if width > height:
                new_width = max_size
                new_height = int((max_size / width) * height)
            else:
                new_height = max_size
                new_width = int((max_size / height) * width)
            
            new_size = (new_width, new_height)
            resized_image = image.resize(new_size)
            format = image.format or 'JPEG'
            img_byte_arr = io.BytesIO()
            resized_image.save(img_byte_arr, format=format)
            img_byte_arr.seek(0)
            
            destination_key = f'resized/{source_key}'
            s3_client.put_object(Bucket=destination_bucket, Key=destination_key, Body=img_byte_arr, ContentType='image/jpeg')
            
            uploaded_uri = f's3://{destination_bucket}/{destination_key}'

        except Exception as e:
            print(f'Error during the image resizing: {e}')
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Image successfully resized',
            'uri': uploaded_uri
        })
    }

