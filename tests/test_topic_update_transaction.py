import pytest
from unittest.mock import MagicMock
from hedera_sdk_python.consensus.topic_update_transaction import TopicUpdateTransaction
from hedera_sdk_python.consensus.topic_id import TopicId
from hedera_sdk_python.account.account_id import AccountId
from hedera_sdk_python.crypto.private_key import PrivateKey
from hedera_sdk_python.client.client import Client
from hedera_sdk_python.response_code import ResponseCode
from hedera_sdk_python.hapi.services import transaction_receipt_pb2
from hedera_sdk_python.transaction.transaction_receipt import TransactionReceipt
from hedera_sdk_python.transaction.transaction_id import TransactionId
from hedera_sdk_python.hapi.services import timestamp_pb2 as hapi_timestamp_pb2

@pytest.mark.usefixtures("mock_account_ids")
def test_build_topic_update_transaction_body(mock_account_ids):
    """
    Test building a TopicUpdateTransaction body with valid topic ID and memo.
    """
    _, _, node_account_id, _, _ = mock_account_ids
    topic_id = TopicId(0,0,1234)
    tx = TopicUpdateTransaction(topic_id=topic_id, memo="Updated Memo")

    tx.operator_account_id = AccountId(0, 0, 2)
    tx.node_account_id = node_account_id

    transaction_body = tx.build_transaction_body()
    assert transaction_body.consensusUpdateTopic.topicID.topicNum == 1234
    assert transaction_body.consensusUpdateTopic.memo.value == "Updated Memo"

def test_missing_topic_id_in_update(mock_account_ids):
    """
    Test that building fails if no topic ID is provided.
    """
    _, _, node_account_id, _, _ = mock_account_ids

    tx = TopicUpdateTransaction(topic_id=None, memo="No ID")
    tx.operator_account_id = AccountId(0, 0, 2)
    tx.node_account_id = node_account_id

    with pytest.raises(ValueError, match="Missing required fields"):
        tx.build_transaction_body()

def test_sign_topic_update_transaction(mock_account_ids):
    """
    Test signing the TopicUpdateTransaction with a private key.
    """
    _, _, node_account_id, _, _ = mock_account_ids
    topic_id = TopicId(0,0,9999)
    tx = TopicUpdateTransaction(topic_id=topic_id, memo="Signature test")
    tx.operator_account_id = AccountId(0, 0, 2)
    tx.node_account_id = node_account_id

    private_key = PrivateKey.generate()

    body_bytes = tx.build_transaction_body().SerializeToString()
    tx.transaction_body_bytes = body_bytes

    tx.sign(private_key)
    assert len(tx.signature_map.sigPair) == 1

def test_execute_topic_update_transaction(mock_account_ids):
    """
    Test executing the TopicUpdateTransaction with a mock Client.
    """
    _, _, node_account_id, _, _ = mock_account_ids
    topic_id = TopicId(0,0,9999)
    tx = TopicUpdateTransaction(topic_id=topic_id, memo="Exec update")
    tx.operator_account_id = AccountId(0, 0, 2)

    client = MagicMock(spec=Client)
    client.operator_private_key = PrivateKey.generate()
    client.operator_account_id = AccountId(0, 0, 2)
    client.node_account_id = node_account_id

    real_tx_id = TransactionId(
        account_id=AccountId(0, 0, 2),
        valid_start=hapi_timestamp_pb2.Timestamp(seconds=12345, nanos=6789)
    )
    client.generate_transaction_id.return_value = real_tx_id

    client.topic_stub = MagicMock()
    mock_response = MagicMock()
    mock_response.nodeTransactionPrecheckCode = ResponseCode.OK
    client.topic_stub.updateTopic.return_value = mock_response

    proto_receipt = transaction_receipt_pb2.TransactionReceipt(status=ResponseCode.OK)
    real_receipt = TransactionReceipt.from_proto(proto_receipt)
    client.get_transaction_receipt.return_value = real_receipt

    receipt = tx.execute(client)

    client.topic_stub.updateTopic.assert_called_once()
    assert receipt is not None
    assert receipt.status == ResponseCode.OK
    print("Test passed: TopicUpdateTransaction executed successfully.")
