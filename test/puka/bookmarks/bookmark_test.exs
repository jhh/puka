defmodule Puka.Bookmarks.BookmarkTest do
  use Puka.DataCase

  alias Puka.Bookmarks
  alias Puka.Repo
  alias Puka.Tags.Tag

  @valid_attrs %{
    "title" => "Docs",
    "url" => "https://example.com"
  }

  test "create_bookmark/1 parses tags and normalizes case" do
    {:ok, bookmark} =
      Bookmarks.create_bookmark(Map.put(@valid_attrs, "tags", " Elixir, phoenix, ELIXIR "))

    bookmark = Bookmarks.get_bookmark!(bookmark.id)
    tag_names = bookmark.tags |> Enum.map(& &1.name) |> Enum.sort()

    assert tag_names == ["elixir", "phoenix"]
    assert Repo.aggregate(Tag, :count, :id) == 2
  end

  test "create_bookmark/1 ignores blank tags" do
    {:ok, bookmark} =
      Bookmarks.create_bookmark(Map.put(@valid_attrs, "tags", " , ,   "))

    bookmark = Bookmarks.get_bookmark!(bookmark.id)
    assert bookmark.tags == []
    assert Repo.aggregate(Tag, :count, :id) == 0
  end

  test "change_bookmark/2 preserves preloaded tags without inserting" do
    {:ok, bookmark} =
      Bookmarks.create_bookmark(Map.put(@valid_attrs, "tags", "elixir"))

    bookmark = Bookmarks.get_bookmark!(bookmark.id)
    tag_count = Repo.aggregate(Tag, :count, :id)

    changeset = Bookmarks.change_bookmark(bookmark, %{})

    # No additional tags inserted during change_bookmark
    assert Repo.aggregate(Tag, :count, :id) == tag_count

    tag_names =
      Ecto.Changeset.get_field(changeset, :tags)
      |> Enum.map(& &1.name)

    assert tag_names == ["elixir"]
  end
end
