import boto3
from variables import RoleArn

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
            print("[INFO] Key: " + itag['Key'] + " Value: " + itag['Value'])
        else:
            print("[INFO]: Skipping Tag: - Key: " + itag['Key'])

    return temptags


instances = ec2.instances.all()
for instance in instances:
    for volume in instance.volumes.all():
        if dryRun:
            print("[VOLUME] " + str(volume) + " [INSTANCE] " + str(instance))
            copythetags(instance)
        else:
            print("[VOLUME]  " + str(volume) + " [INSTANCE] " + str(instance))
            tag = volume.create_tags(Tags=copythetags(instance))
