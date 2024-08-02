

class NotEnoughFundsError(Exception):
    def __init__(self, account_id: int) -> None:
        super().__init__(f"Account {account_id} does not have enough money")


def get_balance(ctx, account):
    conn = ctx.deps.get("conn")
    resp = conn.execute("SELECT balance FROM accounts WHERE account_id = ?", (account,)).fetchone()
    conn.commit()
    return resp[0]


def set_balance(ctx, account, amount):
    conn = ctx.deps.get("conn")
    resp = conn.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, account))
    ctx.assert_statement(resp.rowcount == 1, msg="More that one row was affected")
    conn.commit()


def transfer(ctx, source, target, amount):

    balance = yield ctx.call(get_balance, account=source)

    if balance - amount < 0:
        raise NotEnoughFundsError(account_id=source)

    yield ctx.call(set_balance, source, -1 * amount)

    yield ctx.call(set_balance, target, +1 * amount)

    return source, target, amount