import json
import numpy as np

def lambda_handler(event, context):
    try:
        matrice = event['matrix']
        matrice_np = np.array(matrice)   
        inversa_np = np.linalg.inv(matrice_np)
        inversa_np = np.round(inversa_np, 4)
        inversa_lista = inversa_np.tolist()
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'inversa': inversa_lista
            })
        }
    except np.linalg.LinAlgError:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Matrix not invertible.'
            })
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    return response

