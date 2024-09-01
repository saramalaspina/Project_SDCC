import numpy as np
import json

def lambda_handler(event, context):
    try:
        data = event['data']
        
        if 'X' not in data or 'y' not in data:
            raise ValueError("Invalid input.")
        
        X = np.array(data['X'])
        y = np.array(data['y'])

        if X.shape[0] != y.shape[0]:
            raise ValueError("The number of rows in X must be equal to the number of elements in y.")
        
        X_with_intercept = np.hstack((np.ones((X.shape[0], 1)), X))
        
        linear_regression_lambda = lambda X, y: np.linalg.lstsq(X, y, rcond=None)[0]
        
        coefficients = linear_regression_lambda(X_with_intercept, y)

        response = {
            'statusCode': 200,
            'body': json.dumps({
                'coefficients': coefficients.tolist()  
            })
        }
    
    except Exception as e:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    return response
