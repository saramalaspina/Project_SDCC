import sys
import json
import ast
import boto3
from botocore.exceptions import NoCredentialsError
import os


def fibonacci():
    while True:
        try:
            num = input("Enter the number for which you want to calculate the Fibonacci number (or 'q' to go back): ")
            if num == 'q':
                print("Exiting the function.")
                break
            n = int(num)
            if n < 1 or n > 10000:
                print("Invalid choice. Please try again.")
            else:
                data = {"n": n}
                event = {
                    "function_name": "Fibonacci",
                    "params": data
                }
                event_data = json.dumps(event)
                return event_data
        except ValueError:
            print("Invalid input. Please enter an integer value.")


def inverseMatrix():
    while True:
        try:
            matrix = input("Enter the matrix for the chosen function (e.g. [[1, 2], [3, 4]]) (or 'q' to go back): ")

            if matrix == 'q':
                print("Exiting the function.")
                return None
            
            input_matrix = ast.literal_eval(matrix)
            
            if not isinstance(input_matrix, list) or not all(isinstance(row, list) for row in input_matrix):
                raise ValueError("Input is not a valid matrix.")
            elif not all(len(row) == len(input_matrix) for row in input_matrix):
                raise ValueError("The matrix is not square.")
            elif not (2 <= len(input_matrix) <= 50):
                raise ValueError("The matrix size is not between 2x2 and 50x50.")
            else: 
                data = {"matrix": input_matrix}
                event = {
                    "function_name": "InverseMatrix",
                    "params": data
                }
                event_data = json.dumps(event)
                return event_data
        except (ValueError, SyntaxError) as e:
            print(f"Invalid matrix: {e}")
        

def linearRegression():
    while True:
        try:
            x_input = input("Enter the list X (e.g. [[1, 2, 3], [4, 5, 6]]) (or 'q' to go back): ")
            if x_input == 'q':
                print("Exiting the function.")
                return None
            
            x_list = ast.literal_eval(x_input)
            
            if not isinstance(x_list, list) or not all(isinstance(row, list) for row in x_list):
                raise ValueError("Input X is not a valid list of lists.")
            
            num_columns = len(x_list[0]) if x_list else 0
            
            if not all(len(row) == num_columns for row in x_list):
                raise ValueError("All rows in X must have the same number of columns.")
            if not (1 <= num_columns <= 1000):
                raise ValueError("The number of columns in X must be between 1 and 1000.")
            

            y_input = input("Enter the list y (e.g., [1, 2, 3]): ")
            y_list = ast.literal_eval(y_input)
            
            if not isinstance(y_list, list) or not all(isinstance(elem, (int, float)) for elem in y_list):
                raise ValueError("Input y is not a valid list of numbers.")
            
            if len(y_list) != len(x_list):
                raise ValueError("The number of elements in y must match the number of rows in X.")
        
            data = {
                "data": {
                    "X": x_list,
                    "y": y_list
                }
            }
            event = {
                "function_name": "LinearRegression",
                "params": data
            }
            event_data = json.dumps(event)
            return event_data
        
        except (ValueError, SyntaxError) as e:
            print(f"Invalid input: {e}")



def imageResizing():
    while True:
        try:
            path = input("Enter the path of the image (or 'q' to go back): ")

            if path == 'q':
                print("Exiting the function.")
                return None

            if os.path.exists(path):
                if not os.path.isfile(path):
                     raise ValueError("The path doesn't contain a file")
            else:
                raise ValueError("The file doesn't exist")

            file_key = uploadImageToS3(path)

            data = {
                "Records": [{
                    "s3": {
                        "bucket": {
                            "name": 'imgsource-bucket'
                        },
                        "object": {
                            "key": file_key
                        }
                    }
                }]
            }

            event = {
                "function_name": "ImageResizing",
                "params": data
            }
            event_data = json.dumps(event)
            return event_data

        except Exception as e:
            print(f"Error: {e}")


def uploadImageToS3(path):
    bucket_name = 'imgsource-bucket'
    file_key = path.split('/')[-1]

    credentials = load_aws_credentials('requirements.txt')

    s3 = boto3.client(
        's3',
        aws_access_key_id=credentials.get('aws_access_key_id'),
        aws_secret_access_key=credentials.get('aws_secret_access_key'),
        aws_session_token=credentials.get('aws_session_token'),
        region_name='us-east-1'
    )
    try:
        s3.upload_file(path, bucket_name, file_key)
        return file_key
    except FileNotFoundError:
        print(f"File {file_name} not found")
        return None
    except NoCredentialsError:
        print("Credentials not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def invokeLambda(event):

    credentials = load_aws_credentials('requirements.txt')
        
    client = boto3.client(
        'lambda',
        aws_access_key_id=credentials.get('aws_access_key_id'),
        aws_secret_access_key=credentials.get('aws_secret_access_key'),
        aws_session_token=credentials.get('aws_session_token'),
        region_name='us-east-1'
    )

    response = client.invoke(
        FunctionName='Scheduler',
        InvocationType='RequestResponse',
        Payload=event
    )

    response_payload = response['Payload'].read().decode('utf-8')
    response_data = json.loads(response_payload)

    return response_data

def load_aws_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            credentials[key] = value
    return credentials

def main():

    while True:
        print("Choose a function:")
        print("1: Fibonacci")
        print("2: Inverse Matrix")
        print("3: Image Resizing")
        print("4: Coefficients Linear Regression")
        print("q: Quit")

        choice = input("Enter the number of the function (or 'q' to quit): ")

        if choice == 'q':
            print("Exiting the program.")
            break

        functions = {
            '1': fibonacci,
            '2': inverseMatrix,
            '3': imageResizing,
            '4': linearRegression
        }

        if choice not in functions:
            print("Invalid choice. Please try again.")
            continue
        else:
            selected_function = functions.get(choice)
            event = selected_function()
            if(event == None):
                continue
            response = invokeLambda(event)
            body = json.loads(response['body'])
            region = body['region']
            result = body['response']
            print(f"Region: {region}")
            print(f"Result: {result}")

if __name__ == "__main__":
    main()
