from hedera_sdk_python.consensus.topic_id import TopicId
from hedera_sdk_python.account.account_id import AccountId
from hedera_sdk_python.tokens.token_id import TokenId
from hedera_sdk_python.hbar import Hbar
from hedera_sdk_python.transaction.transfer_transaction import TransferTransaction
from hedera_sdk_python.transaction.transaction_id import TransactionId

def build_query_payment_transaction(
    payer_account_id: AccountId,
    payer_private_key,
    node_account_id: AccountId,
    amount: Hbar
):
    """
    Build and sign a TransferTransaction that sends `amount` of HBAR from
    `payer_account_id` to `node_account_id`. Returns a Transaction proto
    that can be attached to QueryHeader.payment.
    """

    tx = TransferTransaction()
    tx.add_hbar_transfer(payer_account_id, -amount.to_tinybars())
    tx.add_hbar_transfer(node_account_id, amount.to_tinybars())

    tx.transaction_fee = 100_000_000 
    tx.node_account_id = node_account_id
    tx.transaction_id = TransactionId.generate(payer_account_id)

    body_bytes = tx.build_transaction_body().SerializeToString()
    tx.transaction_body_bytes = body_bytes

    tx.sign(payer_private_key)
    return tx.to_proto()
