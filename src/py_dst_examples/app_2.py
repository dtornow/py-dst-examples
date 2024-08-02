

class NotEnoughFundsError(Exception):
    def __init__(self, account_id: int) -> None:
        super().__init__(f"Account {account_id} does not have enough money")


class VersionConflict(Exception):
    def __init__(self, account_id: int) -> None:
        super().__init__(f"Version conflict {account_id}")


def get_balance(ctx, account):
    conn = ctx.deps.get("conn")
    resp = conn.execute("SELECT balance, version FROM accounts WHERE account_id = ?", (account,)).fetchone()
    conn.commit()
    return resp[0], resp[1]


def set_balance(ctx, account, amount, version=None):
    conn = ctx.deps.get("conn")
    if version is None:
        resp = conn.execute("UPDATE accounts SET balance = balance + ?, version = version + 1 WHERE account_id = ?", (amount, account))
        conn.commit()
        ctx.assert_statement(resp.rowcount == 1, msg="More that one row was affected")
    else:
        resp = conn.execute("UPDATE accounts SET balance = balance + ?, version = version + 1 WHERE account_id = ? AND version = ?", (amount, account, version))
        conn.commit()
        if resp.rowcount == 0:
            raise VersionConflict(account_id=account)
 

def transfer(ctx, source, target, amount):

    balance, version = yield ctx.call(get_balance, account=source)

    if balance - amount < 0:
        raise NotEnoughFundsError(account_id=source)

    yield ctx.call(set_balance, source, -1 * amount, version)

    yield ctx.call(set_balance, target, +1 * amount)

    return (source, target, amount)