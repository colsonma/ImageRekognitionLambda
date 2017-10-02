import boto3
import os
import pymysql.cursors
import urllib.parse
import json


def fire(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    validate_image = ValidateImage(bucket, key)
    flagged = validate_image.validate()

    UpdateDateBase(key, flagged)


class ValidateImage(object):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

        self.min_confidence = os.environ['MIN_CONFIDENCE']
        self.rekognition = boto3.client('rekognition')

        self.s3 = boto3.client('s3')
        self.get_image()

    def validate(self):
        flagged = False

        try:
            response = self.rekognition.detect_moderation_labels(
                Image={
                    "S3Object": {
                        "Bucket": self.bucket,
                        "Name": self.key
                    }
                },
                MinConfidence=self.min_confidence
            )

            labels = response['ModerationLabels']
            if labels:
                flagged = True

        except Exception as e:
            print(e)
            flagged = True

        return flagged

    def get_image(self):
        image = self.s3.get_object(Bucket=self.bucket, Key=self.key)


class UpdateDateBase(object):
    def __init__(self, name, flagged):
        self.name = name
        self.flagged = flagged
        self.connection = self.connect()
        # https://github.com/PyMySQL/PyMySQL

        self.update()

    def update(self):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `Image_Validation` (`name`, `flagged`) VALUES (%s, %s)"
                cursor.execute(sql, (self.name, self.flagged)) # Create a new record

            # connection is not autocommit by default. So you must commit to save your changes.
            self.connection.commit()
        finally:
            self.connection.close()

    def connect(self):
        # Connect to the database
        return pymysql.connect(host=os.environ['db_host'],
                                     user=os.environ['db_user'],
                                     password=os.environ['db_password'],
                                     db=os.environ['db_database'],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
