from unittest.mock import Mock

import pytest

from marketingflow.repository import UserScopedRepository


def make_query():
    query = Mock()
    query.select.return_value = query
    query.eq.return_value = query
    query.limit.return_value = query
    query.insert.return_value = query
    query.update.return_value = query
    query.delete.return_value = query
    query.execute.return_value = "result"
    return query


def test_create_forces_verified_owner_id():
    query = make_query()
    client = Mock()
    client.table.return_value = query
    repository = UserScopedRepository(client, "verified-user")

    repository.create("clients", {"name": "Client", "owner_id": "attacker"})

    query.insert.assert_called_once_with(
        {"name": "Client", "owner_id": "verified-user"}
    )


def test_update_filters_row_and_owner_and_cannot_change_owner():
    query = make_query()
    client = Mock()
    client.table.return_value = query
    repository = UserScopedRepository(client, "verified-user")

    repository.update("clients", "row-1", {"name": "Updated", "owner_id": "other"})

    query.update.assert_called_once_with({"name": "Updated"})
    assert query.eq.call_args_list == [
        (("id", "row-1"),),
        (("owner_id", "verified-user"),),
    ]


def test_repository_rejects_arbitrary_table_names():
    with pytest.raises(ValueError, match="Unsupported tenant table"):
        UserScopedRepository(Mock(), "user-1").list("auth.users")
