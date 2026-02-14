defmodule Puka.Repo.Migrations.CreateTags do
  use Ecto.Migration

  def change do
    create table(:tags) do
      add :name, :string

      timestamps(type: :utc_datetime)
    end

    create unique_index(:tags, [:name])

    create table(:bookmarks_tags, primary_key: false) do
      add :bookmark_id, references(:bookmarks, on_delete: :delete_all)
      add :tag_id, references(:tags, on_delete: :delete_all)
    end

    create index(:bookmarks_tags, [:bookmark_id])
    create index(:bookmarks_tags, [:tag_id])
    create unique_index(:bookmarks_tags, [:bookmark_id, :tag_id])
  end
end
