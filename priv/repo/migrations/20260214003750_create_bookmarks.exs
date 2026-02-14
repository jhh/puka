defmodule Puka.Repo.Migrations.CreateBookmarks do
  use Ecto.Migration

  def up do
    create table(:bookmarks) do
      add :title, :string, null: false
      add :description, :text
      add :url, :string, unique: true, null: false
      add :active, :boolean, default: true, null: false

      timestamps(type: :utc_datetime)
    end

    execute """
      ALTER TABLE bookmarks
        ADD COLUMN searchable tsvector
        GENERATED ALWAYS AS (
          setweight(to_tsvector('english', title), 'A') ||
          setweight(to_tsvector('english', coalesce(description, '')), 'B')
        ) STORED;
    """

    execute """
      CREATE INDEX bookmarks_searchable_index ON bookmarks USING gin(searchable);
    """

    create unique_index(:bookmarks, [:url])
  end

  def down do
    drop table(:bookmarks)
  end
end
