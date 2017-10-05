import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # copy object to the bucket in the correct region
        s3.copy_object(Bucket='validate-images', Key=key, CopySource={'Bucket':bucket, 'Key':key})
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and '
              'your bucket is in the same region as this function.'.format(key, bucket))
        raise e
