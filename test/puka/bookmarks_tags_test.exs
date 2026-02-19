defmodule Tagger.BookmarkTest do
  use ExUnit.Case

  alias Puka.Bookmarks
  alias Puka.Bookmarks.Bookmark
  alias Puka.Repo
  alias Puka.Tags.Tag
  import Ecto.Query

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Repo)
  end

  test "creates tags and join rows" do
    params = %{
      "title" => "Docs",
      "url" => "https://example.com",
      "tags" => "elixir, ecto"
    }

    {:ok, bookmark} = Bookmarks.create_bookmark(params)
    bookmark = Repo.preload(bookmark, :tags)

    assert tag_names(bookmark) == ["ecto", "elixir"]
    assert Repo.aggregate(Tag, :count, :id) == 2

    join_count =
      Repo.one(
        from bt in "bookmarks_tags",
          select: count(bt.bookmark_id)
      )

    assert join_count == 2
  end

  test "ignores blank tags" do
    params = %{
      "title" => "No Tags",
      "url" => "https://example.com/blank",
      "tags" => " , ,   "
    }

    {:ok, bookmark} = Bookmarks.create_bookmark(params)
    bookmark = Repo.preload(bookmark, :tags)

    assert bookmark.tags == []
    assert Repo.aggregate(Tag, :count, :id) == 0
  end

  test "dedupes tags and reuses existing tag" do
    Repo.insert!(%Tag{name: "elixir"})

    params = %{
      "title" => "Dupes",
      "url" => "https://example.com/dupes",
      "tags" => "elixir, elixir,  elixir"
    }

    {:ok, bookmark} = Bookmarks.create_bookmark(params)
    bookmark = Repo.preload(bookmark, :tags)

    assert tag_names(bookmark) == ["elixir"]
    assert Repo.aggregate(Tag, :count, :id) == 1
  end

  test "replaces tags on update" do
    {:ok, bookmark} =
      Bookmarks.create_bookmark(%{
        "title" => "Replace",
        "url" => "https://example.com/replace",
        "tags" => "elixir, ecto"
      })

    bookmark = Repo.preload(bookmark, :tags)

    {:ok, bookmark} =
      Bookmarks.update_bookmark(bookmark, %{"tags" => "phoenix"})

    bookmark = Repo.preload(bookmark, :tags)

    assert tag_names(bookmark) == ["phoenix"]

    join_count =
      Repo.one(
        from bt in "bookmarks_tags",
          where: bt.bookmark_id == ^bookmark.id,
          select: count(bt.bookmark_id)
      )

    assert join_count == 1
  end

  defp tag_names(%Bookmark{tags: tags}) do
    tags
    |> Enum.map(& &1.name)
    |> Enum.sort()
  end
end
