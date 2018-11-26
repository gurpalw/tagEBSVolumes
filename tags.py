import boto3
import logging
from variables import RoleArn
from time import strftime
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(strftime("/var/tmp/tagEBSVolume_%H_%M_%m_%d_%Y.log"))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

sts_client = boto3.client('sts')

assumedRoleObject = sts_client.assume_role(
    RoleArn=RoleArn,
    RoleSessionName="AssumeRoleSession1"
)

# From the response that contains the assumed role, get the temporary
# credentials that can be used to make subsequent API calls
credentials = assumedRoleObject['Credentials']

# Use the temporary credentials that AssumeRole returns to make a
# connection to Amazon S3
ec2 = boto3.resource(
    'ec2',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

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
            print("[INFO] Copying Tag...")
            logger.info('Copying Tag...')
            print("[INFO] Key: " + itag['Key'] + " Value: " + itag['Value'])
            logger.info("Key: " + itag['Key'] + " Value: " + itag['Value'])
        else:
            print("[INFO]: Skipping Tag: - Key: " + itag['Key'])
            logger.info("Skipping Tag: - Key: " + itag['Key'])
    return temptags


instances = ec2.instances.all()
count = 0
for instance in instances:
    if instance.tags is not None:
        for volume in instance.volumes.all():
            if dryRun:
                print("[INFO] " + str(volume) + " [INSTANCE] " + str(instance))
                logger.info(str(volume) + " [INSTANCE] " + str(instance))
                copythetags(instance)
            else:
                print("[INFO] Tagging " + str(volume) + " attached to  " + str(instance))
                logger.info("Tagging " + str(volume) + " attached to  " + str(instance))
                tag = volume.create_tags(Tags=copythetags(instance))
                count += 1
                print("[INFO] " + str(count) + " volumes tagged.")
                logger.info(str(count) + " volumes tagged.")
    else:
        print("[INFO] Skipping volumes attached to instance " + str(instance) + " ... no tags.")
        logger.info("Skipping volumes attached to instance " + str(instance) + " ... no tags.")
