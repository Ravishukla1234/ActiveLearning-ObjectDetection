import json
import boto3


def getBucketKey(path):
    bucket = path.split('/')[2]
    suff = path.split('/')[3:]
    key = suff[0]
    for element in suff[1:]:
        if(element != ''):
            key +=  "/" + element
    if(path[-1]=='/'):
        key+='/'
    return bucket,key
    
def downloadImages(manifest_path, tempPath):
    s3 = boto3.client('s3')
    s3Copy = boto3.resource('s3')
    d_bucket,d_key = getBucketKey(tempPath)
    #print(d_bucket,d_key)
    manifest_bucket, manifest_key = getBucketKey(manifest_path)
    result = s3.list_objects(Bucket = manifest_bucket, Prefix=manifest_key)
    for o in result.get('Contents'):
        data = s3.get_object(Bucket=manifest_bucket, Key=o.get('Key'))
        contents = data['Body'].read().decode("UTF-8").split("\n")

        for element in contents:
            try:
                source = json.loads(element)

                s_bucket, s_key = getBucketKey(source['source-ref'])
                copy_source = {
                    'Bucket': s_bucket,
                    'Key': s_key
                }
                #print(s_bucket,s_key)
                d_key_total =d_key +  s_key.split('/')[-1]
                #print(d_bucket, d_key_total)
                s3Copy.meta.client.copy(copy_source, d_bucket, d_key_total)
            except:
                #print(element,"ignored")
                continue
def lambda_handler(event, context):
    # TODO implement
    meta_data = event['meta_data']
    s3_temp_path = event['S3TempPath']
    unlabeled_maifest_path = meta_data['UnlabeledS3Uri'] 
    downloadImages(unlabeled_maifest_path, s3_temp_path)
    return meta_data
