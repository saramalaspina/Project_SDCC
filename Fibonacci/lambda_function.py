import json

def lambda_handler(event, context):
    n = int(event.get('n', 0))
    fibonacci_number = fibonacci(n)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'input': n,
            'fibonacci': fibonacci_number
        })
    }

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
