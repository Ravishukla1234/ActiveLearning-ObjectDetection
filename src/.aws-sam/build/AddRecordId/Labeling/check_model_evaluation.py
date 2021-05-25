import json
import boto3

def lambda_handler(event, context):
    client = boto3.client(service_name='sagemaker')
    meta_data = event['meta_data']
    train_job_name = meta_data['training_config']['TrainingJobName']    
    status = client.describe_training_job(TrainingJobName=train_job_name)['FinalMetricDataList']
    
    meta_data['training_config']['evaluation'] = status[3]['Value']
    return meta_data
