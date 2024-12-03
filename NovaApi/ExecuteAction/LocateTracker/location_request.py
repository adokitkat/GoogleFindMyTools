#
#  GoogleFindMyTools - A set of tools to interact with the Google Find My API
#  Copyright © 2024 Leon Böttger. All rights reserved.
#
import asyncio

from Auth.fcm_receiver import FcmReceiver
from NovaApi.ExecuteAction.nbe_execute_action import create_action_request, serialize_action_request
from NovaApi.nova_request import nova_request
from NovaApi.scopes import NOVA_ACTION_API_SCOPE
from NovaApi.util import generate_random_uuid
from ProtoDecoders import DeviceUpdate_pb2
from ProtoDecoders.decoder import print_device_update_protobuf, parse_device_update_protobuf
from example_data_provider import get_example_data

def create_location_request(canonic_device_id, fcm_registration_id, request_uuid):

    actionRequest = create_action_request(canonic_device_id, fcm_registration_id, request_uuid=request_uuid)

    # Random values, can be arbitrary
    actionRequest.action.locateTracker.activationDate.seconds = 1732120060
    actionRequest.action.locateTracker.activationDate.nanos = 0

    actionRequest.action.locateTracker.contributorType = DeviceUpdate_pb2.SpotContributorType.FMDN_ALL_LOCATIONS

    # Convert to hex string
    hex_payload = serialize_action_request(actionRequest)

    return hex_payload


def get_location_data_for_device(canonic_device_id):

    print("[LocationRequest] Requesting location data for device with canonic ID:", canonic_device_id)

    finished_request = False
    request_uuid = generate_random_uuid()

    def handle_location_response(response):
        nonlocal finished_request
        device_update = parse_device_update_protobuf(response)

        if device_update.fcmMetadata.requestUuid == request_uuid:
            print("[LocationRequest] Location request successful. Reponse:")
            print_device_update_protobuf(response)
            finished_request = True
        else:
            print("[LocationRequest] Received response for a different request. Ignoring.")

    fcm_token = FcmReceiver().register_for_location_updates(handle_location_response)

    hex_payload = create_location_request(canonic_device_id, fcm_token, request_uuid)
    nova_request(NOVA_ACTION_API_SCOPE, hex_payload)

    while not finished_request:
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

if __name__ == '__main__':
    get_location_data_for_device(get_example_data("sample_canonic_device_id"))