defmodule Puka.Bookmarks.BookmarkTest do
  use Puka.DataCase

  alias Puka.Bookmarks.Bookmark
  alias Puka.Repo
  alias Puka.Tags.Tag

  @valid_attrs %{
    "title" => "Docs",
    "url" => "https://example.com"
  }

  test "changeset/3 parses tags and normalizes case" do
    changeset =
      Bookmark.changeset(%Bookmark{}, Map.put(@valid_attrs, "tags", " Elixir, phoenix, ELIXIR "))

    tag_names =
      changeset.changes[:tags]
      |> Enum.map(&Ecto.Changeset.get_field(&1, :name))
      |> Enum.sort()

    assert tag_names == ["elixir", "phoenix"]
    assert Repo.aggregate(Tag, :count, :id) == 2
  end

  test "changeset/3 ignores blank tags" do
    changeset = Bookmark.changeset(%Bookmark{}, Map.put(@valid_attrs, "tags", " , ,   "))

    assert changeset.changes[:tags] == []
    assert Repo.aggregate(Tag, :count, :id) == 0
  end

  test "changeset/3 with skip_tag_parse avoids tag inserts" do
    tag_count = Repo.aggregate(Tag, :count, :id)

    changeset =
      Bookmark.changeset(%Bookmark{}, Map.put(@valid_attrs, "tags", "elixir"),
        skip_tag_parse: true
      )

    assert Repo.aggregate(Tag, :count, :id) == tag_count
    refute Map.has_key?(changeset.changes, :tags)
  end
end
