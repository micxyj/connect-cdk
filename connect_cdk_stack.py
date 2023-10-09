from aws_cdk import (
    # Duration,
    Stack,
    CfnTag
    # aws_sqs as sqs,
)
from constructs import Construct
from aws_cdk import aws_connect as connect
import os
import subprocess
import streamlit as st
import pandas as pd
import boto3
import time
from PIL import Image


# setting work dir
# 需要填写绝对路径
os.chdir('YOUR_PATH/connect-cdk-example/')


# app title
col1, col2 = st.columns([1, 10])
image = Image.open('./logo.png')
with col1:
    st.image(image, use_column_width='always')
with col2:
    header = f"Amazon Connect Deployment Tool!"
    st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)

# add connect agents
st.subheader('Agents Configuration', divider="rainbow")
uploaded_file = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
    df.to_csv("agents.csv", index=False)

# st.divider()

# connect instance configuration
st.subheader('Connect Parameters', divider="rainbow")
connect_instance_arn = st.text_input('Amazon Connect instance ARN', value="")

# security profile configuration
security_profile_arn = st.text_input('Security profile ARN', value="")

# hours of operation configuration
hop_arn = st.text_input('Hours of operation ARN', value="")

# hours of operation configuration
tenant_name = st.text_input('Tenant Name (Required)')

# save env
st.write('*You must click follow button to save configuration*')
if st.button('Save Configuration'):
    os.environ["connect_instance_arn"] = connect_instance_arn
    os.environ["security_profile_arn"] = security_profile_arn
    os.environ["hop_arn"] = hop_arn
    os.environ["tenant_name"] = tenant_name
    st.success("ENV has been set")

# st.divider()

# deploy cdk
st.subheader('CDK Deployment', divider="rainbow")
if st.button('Deploy CDK Stack'):
    subprocess.Popen(['cdk', 'deploy'])
    st.write('CDK stack initialized...........')
    time.sleep(5)
    with st.spinner('Deploying......'):
        cfm_client = boto3.client("cloudformation")
        try:
            while True:
                time.sleep(5)
                res = cfm_client.describe_stacks()
                stacks = [i['StackName'] for i in res['Stacks']]
                if os.environ["tenant_name"] in stacks:
                    res = cfm_client.describe_stacks(StackName=os.environ["tenant_name"])
                    status = res['Stacks'][0]['StackStatus']
                    if status == 'CREATE_COMPLETE':
                        st.success('Deploy complete!')
                        break
                    elif status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                        st.error('Deploy failed, please check CloudFormation event for detailed messages.')
                        break
                    else:
                        continue
        except Exception as e:
            st.error('Failed')

# destroy cdk
st.subheader('Clean Resources', divider="rainbow")
if st.button('Destroy CDK Stack'):
    subprocess.Popen(['cdk', 'destroy', '--force'])
    st.write('Destroying CDK stack...........')
    time.sleep(5)
    with st.spinner('Destroying......'):
        cfm_client = boto3.client("cloudformation")
        try:
            while True:
                time.sleep(5)
                res = cfm_client.describe_stacks()
                stacks = [i['StackName'] for i in res['Stacks']]
                if os.environ["tenant_name"] not in stacks:
                    st.success('Destroy complete!')
                    break
                else:
                    res = cfm_client.describe_stacks(StackName=os.environ["tenant_name"])
                    status = res['Stacks'][0]['StackStatus']
                    if status == 'DELETE_FAILED':
                        st.error('Destroy failed, please check CloudFormation event for detailed messages.')
                        break
                    else:
                        continue
        except Exception as e:
            st.error('Failed')


class ConnectCdkExampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # parameter
        connect_instance_arn = os.environ["connect_instance_arn"]
        security_profile_arn = os.environ["security_profile_arn"]
        hop_arn = os.environ["hop_arn"]
        count = 1
        df = pd.read_csv("agents.csv")

        # define phone number
        cfn_phone_number = connect.CfnPhoneNumber(self, "CfnPhoneNumber",
            country_code="US",
            target_arn=connect_instance_arn,
            type="DID",

            # the properties below are optional
            description="phone number created using cfn",
            tags=[CfnTag(
                key="testkey",
                value="testValue"
            )]
        )

        # define IVR
        # 需要填写 content 参数，入参为 connect flow
        cfn_contact_flow = connect.CfnContactFlow(self, "CfnContactFlow",
            content="",
            instance_arn=connect_instance_arn,
            name=os.environ["tenant_name"]+"CfnFlow",
            type="CONTACT_FLOW",

            # the properties below are optional
            description="flow created using cfn",
            tags=[CfnTag(
                key="testkey",
                value="testValue"
            )]
        )

        # define queue
        cfn_queue = connect.CfnQueue(self, "CfnQueue",
            hours_of_operation_arn=hop_arn,
            instance_arn=connect_instance_arn,
            name="CfnQueue",

            # the properties below are optional
            description="queue created using cfn",
            outbound_caller_config=connect.CfnQueue.OutboundCallerConfigProperty(
                outbound_caller_id_number_arn=cfn_phone_number.attr_phone_number_arn,
            ),
            tags=[CfnTag(
                key="testkey",
                value="testValue"
            )]
        )

        # define routing profile
        cfn_routing_profile = connect.CfnRoutingProfile(self, "CfnRoutingProfile",
            default_outbound_queue_arn=cfn_queue.attr_queue_arn,
            description="routing profile created using cfn",
            instance_arn=connect_instance_arn,
            media_concurrencies=[
                connect.CfnRoutingProfile.MediaConcurrencyProperty(
                channel="VOICE",
                concurrency=1,),
                connect.CfnRoutingProfile.MediaConcurrencyProperty(
                channel="CHAT",
                concurrency=1,)
                ],
            name="CfnRoutingProfile",

            # the properties below are optional
            queue_configs=[connect.CfnRoutingProfile.RoutingProfileQueueConfigProperty(
                delay=0,
                priority=1,
                queue_reference=connect.CfnRoutingProfile.RoutingProfileQueueReferenceProperty(
                    channel="VOICE",
                    queue_arn=cfn_queue.attr_queue_arn
                )
            )],
            tags=[CfnTag(
                key="testkey",
                value="testValue"
            )]
        )

        # define agents
        for index, row in df.iterrows():
            cfn_user = connect.CfnUser(self, "CfnUser"+str(count),
                instance_arn=connect_instance_arn,
                phone_config=connect.CfnUser.UserPhoneConfigProperty(
                    phone_type="SOFT_PHONE",

                    # the properties below are optional
                    auto_accept=False,
                ),
                routing_profile_arn=cfn_routing_profile.attr_routing_profile_arn,
                security_profile_arns=[security_profile_arn],
                username=row["Username"],

                # the properties below are optional
                identity_info=connect.CfnUser.UserIdentityInfoProperty(
                    first_name=row["FirstName"],
                    last_name=row["LastName"],
                ),
                password="Aa12345678.",
                tags=[CfnTag(
                    key="testkey",
                    value="testValue"
                )]
            )
            count += 1