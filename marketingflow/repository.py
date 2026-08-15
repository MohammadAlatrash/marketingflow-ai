"""User-scoped Supabase repository with defense-in-depth ownership filters."""

from typing import Any


TENANT_TABLES = {
    "clients",
    "brand_documents",
    "brand_chunks",
    "campaigns",
    "content_items",
    "feedback",
}


class UserScopedRepository:
    def __init__(self, client: Any, owner_id: str):
        if not owner_id:
            raise ValueError("A verified owner_id is required.")
        self.client = client
        self.owner_id = owner_id

    def list(self, table: str, *, limit: int = 100):
        return (
            self._table(table)
            .select("*")
            .eq("owner_id", self.owner_id)
            .limit(min(max(limit, 1), 500))
            .execute()
        )

    def create(self, table: str, values: dict[str, Any]):
        payload = {**values, "owner_id": self.owner_id}
        return self._table(table).insert(payload).execute()

    def update(self, table: str, row_id: str, values: dict[str, Any]):
        payload = {key: value for key, value in values.items() if key != "owner_id"}
        return (
            self._table(table)
            .update(payload)
            .eq("id", row_id)
            .eq("owner_id", self.owner_id)
            .execute()
        )

    def delete(self, table: str, row_id: str):
        return (
            self._table(table)
            .delete()
            .eq("id", row_id)
            .eq("owner_id", self.owner_id)
            .execute()
        )

    def _table(self, table: str):
        if table not in TENANT_TABLES:
            raise ValueError(f"Unsupported tenant table: {table}")
        return self.client.table(table)
