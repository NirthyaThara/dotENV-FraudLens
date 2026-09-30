from .models import EvaluationContext, Transaction

def build_context(transaction: Transaction, history: list[Transaction]) -> EvaluationContext:
    relevant = [
        tx for tx in history
        if tx.user_id == transaction.user_id
        and tx.transaction_ref != transaction.transaction_ref
        and tx.transaction_time <= transaction.transaction_time
    ]
    return EvaluationContext(current=transaction, history=relevant)
