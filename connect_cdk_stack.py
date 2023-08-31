from aws_cdk import (
    # Duration,
    Stack,
    CfnTag
    # aws_sqs as sqs,
)
from constructs import Construct
from aws_cdk import aws_connect as connect

class ConnectCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # parameter
        connect_instance_arn = ''
        security_profile_arn = ''
        hop_arn = ''
        agents = [
            {
                "FirstName": "kevin",
                "LastName": "li",
                "Username": "kevin"
            },
            {
                "FirstName": "felix",
                "LastName": "wang",
                "Username": "felix"
            },
        ]
        count = 1

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
        cfn_contact_flow = connect.CfnContactFlow(self, "CfnContactFlow",
            content="",
            instance_arn=connect_instance_arn,
            name="CfnFlow",
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
        for agent in agents:
            cfn_user = connect.CfnUser(self, "CfnUser"+str(count),
                instance_arn=connect_instance_arn,
                phone_config=connect.CfnUser.UserPhoneConfigProperty(
                    phone_type="SOFT_PHONE",

                    # the properties below are optional
                    auto_accept=False,
                ),
                routing_profile_arn=cfn_routing_profile.attr_routing_profile_arn,
                security_profile_arns=[security_profile_arn],
                username=agent["Username"],

                # the properties below are optional
                identity_info=connect.CfnUser.UserIdentityInfoProperty(
                    first_name=agent["FirstName"],
                    last_name=agent["LastName"],
                ),
                password="Aa12345678.",
                tags=[CfnTag(
                    key="testkey",
                    value="testValue"
                )]
            )
            count += 1