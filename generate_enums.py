from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
import os

SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
SECRET = os.environ["SECRET"]
TENANT_ID = os.environ["TENANT_ID"]

CREDS = ClientSecretCredential(client_id=CLIENT_ID, client_secret=SECRET,
                               tenant_id=TENANT_ID)


def main():
    enum_file = f'from enum import Enum{add_instance_and_region_enums()}'

    # Create file
    with open("azure_enums/azure_enums.py", 'w') as output_file:
        output_file.write(enum_file)


def add_instance_and_region_enums() -> str:
    instance_blob = f"\n\nclass AzureInstanceTypes(Enum):"
    region_blob = f"\n\nclass AzureRegions(Enum):"

    sub_client = SubscriptionClient(CREDS)
    locations = sub_client.subscriptions.list_locations(SUBSCRIPTION_ID)

    compute_client = ComputeManagementClient(
        credential=CREDS,
        subscription_id=SUBSCRIPTION_ID
    )

    vm_set = set()

    for location in locations:
        region = location.name

        region_blob = f"{region_blob}\n    {region} = '{region}'"

        try:
            vms = compute_client.virtual_machine_sizes.list(location.name)

            for vm in vms:
                vm_set.add(vm.name)
        # Azure sucks and its APIs dont recognize each other
        # If exceptionl ignore its not a big deal
        except Exception as e:
            print(e)

    for instance in vm_set:
        instance_type = instance

        instance_enum = instance_type.upper().replace('-', '_')
        instance_type = f"'{instance_type}'"

        instance_blob = f"{instance_blob}\n    {instance_enum} = {instance_type}"

    return f"{instance_blob}\n{region_blob}"


if __name__ == '__main__':
    main()
