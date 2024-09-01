# Carbon aware scheduling of serverless workflows

This repository contains the final project for the course of Distributed Systems and Cloud Computing of the University of Rome Tor Vergata (faculty Computer Engineering).  

To execute the project follow the next steps:

## Create the AWS Environment

1. Modify the file requirements.txt with the personal information from the AWS account
   
2. Create 5 bucket S3 to store:
      - The state of the round robin used in the Scheduler
      - The carbon information collected from MetricServer
      - The best regions selected from Analyzer
      - The images to resize with ImageResizing
      - The images resized with ImageResizing

3. Modify the name of the buckets in the Lambda functions and the client
   
4. Create the table LambdaProfilingData as the TABLE I shown in the Report at pag. 4
   
5. Create the Lambda functions MetricServer, Scheduler and Analyzer in regione us-east-1 by adding the provided folders as zip file
   
6. Create the Lambda functions Fibonacci, ImageResizing, InverseMatrix and LinearRegression in regions us-east-1 and us-west-2 by adding the provided folders as zip file

## Run the code

1. Open the code project folder in your terminal.

2. Launch the file client.py with the command
   
        python3 client.py
   
