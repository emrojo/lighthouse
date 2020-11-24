from unittest.mock import patch
from lighthouse.messages.message import Message
from lighthouse.helpers.plate_events import (
    construct_event_message,
    get_routing_key,
    construct_source_plate_not_recognised_message,
    construct_source_plate_no_map_data_message,
)
from lighthouse.constants import (
    PLATE_EVENT_SOURCE_COMPLETED,
    PLATE_EVENT_SOURCE_NOT_RECOGNISED,
    PLATE_EVENT_SOURCE_NO_MAP_DATA,
    PLATE_EVENT_SOURCE_ALL_NEGATIVES,
)

# ---------- construct_event_messages tests ----------


def test_construct_event_message_unrecognised_event():
    errors, message = construct_event_message("not a real event", {})

    assert len(errors) == 1
    assert message is None


def test_construct_event_message_source_complete():
    with patch(
        "lighthouse.helpers.plate_events.construct_source_plate_completed_message"
    ) as mock_construct_source_completed_message:
        test_return_value = ([], Message("test message"))
        mock_construct_source_completed_message.return_value = test_return_value

        test_params = {"test_key": "test_value"}
        result = construct_event_message(PLATE_EVENT_SOURCE_COMPLETED, test_params)

        mock_construct_source_completed_message.assert_called_with(test_params)
        assert result == test_return_value


def test_construct_event_message_source_not_recognised():
    with patch(
        "lighthouse.helpers.plate_events.construct_source_plate_not_recognised_message"
    ) as mock_construct_source_not_recognised_message:
        test_return_value = ([], Message("test message"))
        mock_construct_source_not_recognised_message.return_value = test_return_value

        test_params = {"test_key": "test_value"}
        result = construct_event_message(PLATE_EVENT_SOURCE_NOT_RECOGNISED, test_params)

        mock_construct_source_not_recognised_message.assert_called_with(test_params)
        assert result == test_return_value


def test_construct_event_message_source_no_map_data():
    with patch(
        "lighthouse.helpers.plate_events.construct_source_plate_no_map_data_message"
    ) as mock_construct_source_no_map_data_message:
        test_return_value = ([], Message("test message"))
        mock_construct_source_no_map_data_message.return_value = test_return_value

        test_params = {"test_key": "test_value"}
        result = construct_event_message(PLATE_EVENT_SOURCE_NO_MAP_DATA, test_params)

        mock_construct_source_no_map_data_message.assert_called_with(test_params)
        assert result == test_return_value


def test_construct_event_message_source_all_negatives():
    with patch(
        "lighthouse.helpers.plate_events.construct_source_plate_all_negatives_message"
    ) as mock_construct_source_all_negatives_message:
        test_return_value = ([], Message("test message"))
        mock_construct_source_all_negatives_message.return_value = test_return_value

        test_params = {"test_key": "test_value"}
        result = construct_event_message(PLATE_EVENT_SOURCE_ALL_NEGATIVES, test_params)

        mock_construct_source_all_negatives_message.assert_called_with(test_params)
        assert result == test_return_value


# ---------- get_routing_key tests ----------


def test_get_routing_key(app):
    with app.app_context():
        test_event_type = "test_event_type"
        result = get_routing_key(test_event_type)

        assert result == f"test.event.{test_event_type}"


# ---------- construct_source_plate_not_recognised_message tests ----------


def test_construct_source_plate_not_recognised_message_errors_without_user_id():
    test_params = {"robot": "12345"}
    errors, message = construct_source_plate_not_recognised_message(test_params)

    assert len(errors) == 1
    assert message is None

    test_params = {"robot": "12345", "user_id": ""}
    errors, message = construct_source_plate_not_recognised_message(test_params)

    assert len(errors) == 1
    assert message is None


def test_construct_source_plate_not_recognised_message_errors_without_robot():
    test_params = {"user_id": "test_user"}
    errors, message = construct_source_plate_not_recognised_message(test_params)

    assert len(errors) == 1
    assert message is None

    test_params = {"user_id": "test_user", "robot": ""}
    errors, message = construct_source_plate_not_recognised_message(test_params)

    assert len(errors) == 1
    assert message is None


def test_construct_source_plate_not_recognised_message_errors_with_failure_getting_robot_uuid():
    with patch("lighthouse.helpers.plate_events.get_robot_uuid", side_effect=Exception("Boom!")):
        test_params = {"user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_not_recognised_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_not_recognised_message_errors_without_robot_uuid():
    with patch("lighthouse.helpers.plate_events.get_robot_uuid", return_value=None):
        test_params = {"user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_not_recognised_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_not_recognised_message_creates_expected_message(app):
    with app.app_context():
        test_robot_uuid = "adb83afb-d59a-47f2-8d2d-7f71703ca256"
        with patch("lighthouse.helpers.plate_events.get_robot_uuid", return_value=test_robot_uuid):
            with patch("lighthouse.helpers.plate_events.Message") as mock_message:
                test_user_id = "test_user"
                test_robot_serial_number = "12345"
                test_params = {"user_id": test_user_id, "robot": test_robot_serial_number}
                errors, _ = construct_source_plate_not_recognised_message(test_params)

                assert len(errors) == 0

                args, _ = mock_message.call_args
                message_content = args[0]

                assert message_content["lims"] == app.config["RMQ_LIMS_ID"]

                event = message_content["event"]
                assert event["uuid"] is not None
                assert event["event_type"] == PLATE_EVENT_SOURCE_NOT_RECOGNISED
                assert event["occured_at"] is not None
                assert event["user_identifier"] == test_user_id

                subjects = event["subjects"]
                assert len(subjects) == 1
                assert {  # robot subject
                    "role_type": "robot",
                    "subject_type": "robot",
                    "friendly_name": test_robot_serial_number,
                    "uuid": test_robot_uuid,
                } in subjects


# ---------- construct_source_plate_no_map_data_message tests ----------


def test_construct_source_plate_no_map_data_message_errors_without_barcode():
    test_params = {"user_id": "test user", "robot": "12345"}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None

    test_params = {"barcode": "", "user_id": "test user", "robot": "12345"}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None


def test_construct_source_plate_no_map_data_message_errors_without_user_id():
    test_params = {"barcode": "ABC123", "robot": "12345"}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None

    test_params = {"barcode": "ABC123", "user_id": "", "robot": "12345"}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None


def test_construct_source_plate_no_map_data_message_errors_without_user_id():
    test_params = {"barcode": "ABC123", "user_id": "test user"}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None

    test_params = {"barcode": "ABC123", "user_id": "test user", "robot": ""}
    errors, message = construct_source_plate_no_map_data_message(test_params)

    assert len(errors) == 1
    assert message is None


def test_construct_source_plate_no_map_data_message_errors_with_failure_getting_robot_uuid():
    with patch("lighthouse.helpers.plate_events.get_robot_uuid", side_effect=Exception("Boom!")):
        test_params = {"barcode": "ABC123", "user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_no_map_data_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_no_map_data_message_errors_without_robot_uuid():
    with patch("lighthouse.helpers.plate_events.get_robot_uuid", return_value=None):
        test_params = {"barcode": "ABC123", "user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_no_map_data_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_no_map_data_message_errors_with_failure_getting_source_plate_uuid():
    with patch(
        "lighthouse.helpers.plate_events.get_source_plate_uuid", side_effect=Exception("Boom!")
    ):
        test_params = {"barcode": "ABC123", "user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_no_map_data_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_no_map_data_message_errors_without_source_plate_uuid():
    with patch("lighthouse.helpers.plate_events.get_source_plate_uuid", return_value=None):
        test_params = {"barcode": "ABC123", "user_id": "test_user", "robot": "12345"}
        errors, message = construct_source_plate_no_map_data_message(test_params)

        assert len(errors) == 1
        assert message is None


def test_construct_source_plate_no_map_data_message_creates_expected_message(app):
    with app.app_context():
        test_robot_uuid = "adb83afb-d59a-47f2-8d2d-7f71703ca256"
        with patch("lighthouse.helpers.plate_events.get_robot_uuid", return_value=test_robot_uuid):
            test_source_plate_uuid = "3a06a935-0029-49ea-81bc-e5d8eeb1319e"
            with patch(
                "lighthouse.helpers.plate_events.get_source_plate_uuid",
                return_value=test_source_plate_uuid,
            ):
                with patch("lighthouse.helpers.plate_events.Message") as mock_message:
                    test_barcode = "ABC123"
                    test_user_id = "test_user"
                    test_robot_serial_number = "12345"
                    test_params = {
                        "barcode": test_barcode,
                        "user_id": test_user_id,
                        "robot": test_robot_serial_number,
                    }
                    errors, _ = construct_source_plate_no_map_data_message(test_params)

                    assert len(errors) == 0

                    args, _ = mock_message.call_args
                    message_content = args[0]

                    assert message_content["lims"] == app.config["RMQ_LIMS_ID"]

                    event = message_content["event"]
                    assert event["uuid"] is not None
                    assert event["event_type"] == PLATE_EVENT_SOURCE_NO_MAP_DATA
                    assert event["occured_at"] is not None
                    assert event["user_identifier"] == test_user_id

                    subjects = event["subjects"]
                    assert len(subjects) == 2
                    assert {  # robot subject
                        "role_type": "robot",
                        "subject_type": "robot",
                        "friendly_name": test_robot_serial_number,
                        "uuid": test_robot_uuid,
                    } in subjects
                    assert {
                        "role_type": "cherrypicking_source_labware",
                        "subject_type": "plate",
                        "friendly_name": test_barcode,
                        "uuid": test_source_plate_uuid,
                    } in subjects
