import botocore.session
import botocore.credentials
import boto3
import configparser
import json
import datetime
from dateutil.parser import parse
import os

expiration_file = '/app/output/expiration_dates.json'
keys_info = []
profiles = [
    {
        'env_name': 'ecosystem01',
        'user_name': 'apiuser',
        'credentials_file': 'ci/deployments/ecosystem01/aws/credentials',
        'config_file': 'ci/deployments/ecosystem01/aws/config'
    }
]


def create_session(profile, credentials_file, config_file):
    try:
        config = configparser.ConfigParser()
        with open(credentials_file, 'r') as f:
            config.read_file(f)
            access_key = config.get('default', 'aws_access_key_id')
            secret_key = config.get('default', 'aws_secret_access_key')
            region = config.get('default', 'region')

        with open(config_file, 'r') as f:
            config.read_file(f)
            role_arn = config.get('default', 'role_arn')

        session = botocore.session.Session()
        session.set_credentials(access_key, secret_key)
        session.set_config_variable('region', region)  # Set your desired region here

        # Use boto3 to create an STS client and assume the role
        sts_client = boto3.client('sts', aws_access_key_id=session.get_credentials().access_key,
                                  aws_secret_access_key=session.get_credentials().secret_key,
                                  aws_session_token=session.get_credentials().token)

        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="KeyRotation"
        )

        # Update the session with the assumed role's temporary credentials
        session.set_credentials(assumed_role['Credentials']['AccessKeyId'],
                                assumed_role['Credentials']['SecretAccessKey'],
                                assumed_role['Credentials']['SessionToken'])

        return session
    except (configparser.NoOptionError, configparser.NoSectionError):
        print(f"Profile {profile} not found in {credentials_file} or {config_file}")
        return None


def load_expiration_dates():
    if os.path.exists(expiration_file):
        with open(expiration_file, 'r') as f:
            return json.load(f)
    else:
        return {}


def save_expiration_dates(expiration_dates):
    with open(expiration_file, 'w') as f:
        json.dump(expiration_dates, f, default=str, indent=4)


def should_update_access_key(profile):
    expiration_dates = load_expiration_dates()
    if profile not in expiration_dates:
        return True

    expiration_date = parse(expiration_dates[profile])
    now = datetime.datetime.now(datetime.timezone.utc)
    days_since_expiration = (now - expiration_date).days

    return days_since_expiration >= 70


def update_expiration_date(profile, creation_date):
    expiration_dates = load_expiration_dates()
    expiration_dates[profile] = creation_date
    save_expiration_dates(expiration_dates)


def save_new_credentials(profile, access_key, secret_key):
    output_file = f"/app/output/{profile}_new_credentials"
    with open(output_file, 'w') as f:
        f.write("[default]\n")
        f.write(f"region=eu-west-1\n")  # Change the region if needed
        f.write("output=json\n")
        f.write(f"aws_access_key_id={access_key}\n")
        f.write(f"aws_secret_access_key={secret_key}\n")
    print(f"New credentials saved for profile '{profile}' in file '{output_file}'")


def test_s3_query(environment, credential_file, config_file):
    session = create_session(environment, credential_file, config_file)
    s3 = session.create_client('s3')
    # List all the S3 buckets
    response = s3.list_buckets()

    print(f"S3 Buckets for environment '{environment}':")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

    print("\n")


def test_credentials(environment, credential_file, config_file):
    session = create_session(environment, credential_file, config_file)
    sts = session.client('sts')

    try:
        response = sts.get_caller_identity()
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"Failed to get caller identity with status code: {response['ResponseMetadata']['HTTPStatusCode']}")
        print(f"Credentials are valid for profile '{environment}'")
    except Exception as e:
        print(f"Credentials are invalid for profile '{environment}': {e}")
        raise e


def update_aws_keys():
    for profile_data in profiles:
        environment = profile_data['env_name']
        user_name = profile_data['user_name']
        credentials_file = profile_data['credentials_file']
        config_file = profile_data['config_file']

        if not should_update_access_key(environment):
            print(f'Key are not expired and update not required')
            continue

        session = create_session(environment, credentials_file, config_file)
        if session is None:
            continue

        iam = session.create_client('iam')

        # Command 1 - Get access keys for the user
        access_keys = iam.list_access_keys(UserName=user_name)

        # Check if the access key is older than 70 days
        now = datetime.datetime.now(datetime.timezone.utc)
        key_to_update = None
        for key in access_keys['AccessKeyMetadata']:
            age = (now - key['CreateDate']).days
            if age > 70 and key['Status'] == 'Active':
                key_to_update = key
                break

        # Check if there are 2 keys and deactivate the old key as aws will only allow max of 2 access keys
        if key_to_update:
            # Deactivate the oldest key if there are two active keys
            if len(access_keys['AccessKeyMetadata']) == 2:
                oldest_key = min(access_keys['AccessKeyMetadata'], key=lambda k: k['CreateDate'])
                # Command 3
                iam.update_access_key(AccessKeyId=oldest_key['AccessKeyId'], Status='Inactive', UserName=user_name)

            # Create new access_key
            new_key = iam.create_access_key(UserName=user_name)['AccessKey']
            keys_info.append({
                'UserName': new_key['UserName'],
                'AccessKeyId': new_key['AccessKeyId'],
                'SecretAccessKey': new_key['SecretAccessKey']
            })
            save_new_credentials(environment, new_key['AccessKeyId'], new_key['SecretAccessKey'])
            test_credentials(environment, credentials_file, f"/app/output/{environment}_new_credentials")
            # yet to implement rollback
            update_expiration_date(environment, new_key['CreateDate'])

        print(f'Updated AWS keys at {datetime.datetime.now()}')


update_aws_keys()
