import os, pytest, resonate, sqlite3

import py_dst_examples.app_3 as app_3


ACCOUNT = range(5)
BALANCE = 100
TOTAL = len(ACCOUNT) * BALANCE


@pytest.fixture()
def setup_and_teardown():
    # create the database
    conn = sqlite3.connect("test-3.db")
    # sanity check
    assert conn.execute("SELECT 1").fetchone() == (1,)
    conn.execute("CREATE TABLE accounts(account_id, balance, version)")
    conn.execute("CREATE TABLE transfer(transfer_id, account_id, amount)")
    for i in ACCOUNT:
        conn.execute("INSERT INTO accounts VALUES (?, ?, 0)", (i, BALANCE))    
    conn.commit()
    yield conn
    conn.close()
    # delete the database
    os.remove("test-3.db")


@pytest.mark.parametrize("scheduler", resonate.testing.dst([range(50)], mode="concurrent", failure_chance=0.2, max_failures=1000))
def test_race_condition(scheduler, setup_and_teardown):

    conn = setup_and_teardown

    scheduler.deps.set("conn", conn)

    for id in range(100):
        scheduler.add(
            app_3.transfer,
            id,
            source=scheduler.random.choice(ACCOUNT),
            target=scheduler.random.choice(ACCOUNT),
            amount=scheduler.random.randint(0, 150),
        )

    promises = scheduler.run()

    # Invariant #1, no negative balances

    neg = conn.execute("SELECT COUNT(*) FROM accounts WHERE balance < 0").fetchone()[0]

    assert neg == 0, f"Seed: {scheduler.seed} # Neg: Expected 0, actual {neg}"

    # Invariant #2, total balance is preserved

    tot = conn.execute("SELECT SUM(balance) FROM accounts").fetchone()[0]

    assert tot == TOTAL, f"Seed: {scheduler.seed} # Tot: Expected {TOTAL}, actual {tot} "

    # Invariant #3, expected equals actual

    table = {i: BALANCE for i in ACCOUNT}

    for p in promises:
        if p.done():
            try:
                source, target, amount = p.result()
                table[source] -= amount
                table[target] += amount
            except:
                pass

    for i in ACCOUNT:
        balance = conn.execute("SELECT balance FROM accounts WHERE account_id = ?", (i,)).fetchone()[0]
        assert balance == table[i], f"Seed: {scheduler.seed} # Expected {table[i]}, actual {balance} for account {i}"