import boto3
import logging
#from variables import RoleArn
from time import strftime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(strftime("/tmp/tagEBSVolume_%H_%M_%m_%d_%Y.log"))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

sts_client = boto3.client('sts')

#assumedRoleObject = sts_client.assume_role(
  #  RoleArn=RoleArn,
   # RoleSessionName="AssumeRoleSession1"
#)

# From the response that contains the assumed role, get the temporary
# credentials that can be used to make subsequent API calls
#credentials = assumedRoleObject['Credentials']

# Use the temporary credentials that AssumeRole returns to make a
# connection to Amazon S3
ec2 = boto3.resource(
    'ec2')
  #  aws_access_key_id=credentials['AccessKeyId'],
  #  aws_secret_access_key=credentials['SecretAccessKey'],
  #  aws_session_token=credentials['SessionToken'],
#)

dryRun = False


def copythetags(instance):
    viptags = (
        "name", "Name", "project", "Project", "team", "Team", "application", "Application", "environment",
        "Environment")
    temptags = []
    tagdictionary = {}
    for itag in instance.tags:
        if itag['Key'] in viptags:
            tagdictionary['Value'] = itag['Value']
            tagdictionary['Key'] = itag['Key']
            temptags.append(tagdictionary.copy())
            logger.info('Copying Tag...')
            logger.info("Key: " + itag['Key'] + " Value: " + itag['Value'])
        else:
            logger.info("Skipping Tag: - Key: " + itag['Key'])
    return temptags


def lambda_handler(event, context):
    instances = ec2.instances.all()
    count = 0
    for instance in instances:
        if instance.tags is not None:
            for volume in instance.volumes.all():
                if dryRun:
                    logger.info(str(volume) + " [INSTANCE] " + str(instance))
                    copythetags(instance)
                else:
                    logger.info("Tagging " + str(volume) + " attached to  " + str(instance))
                    tag = volume.create_tags(Tags=copythetags(instance))
                    count += 1
                    logger.info(str(count) + " volumes tagged. ")
        else:
            logger.info("Skipping volumes attached to instance " + str(instance) + " ... no tags.")
