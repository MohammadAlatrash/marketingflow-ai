from pathlib import Path


MIGRATION = Path(__file__).resolve().parents[1] / "supabase/migrations/202608160001_foundation.sql"


def test_migration_enables_rls_and_uses_authenticated_owner_policies():
    sql = MIGRATION.read_text()

    for table in (
        "profiles",
        "clients",
        "brand_documents",
        "brand_chunks",
        "campaigns",
        "content_items",
        "feedback",
    ):
        assert f"alter table public.{table} enable row level security" in sql

    assert "to authenticated" in sql
    assert "(select auth.uid()) = owner_id" in sql
    assert "service_role" not in sql


def test_private_storage_policy_is_scoped_to_user_folder():
    sql = MIGRATION.read_text()

    assert "values ('brand-assets', 'brand-assets', false" in sql
    assert "(storage.foldername(name))[1] = (select auth.uid()::text)" in sql
    assert "owner_id = (select auth.uid()::text)" in sql
