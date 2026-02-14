defmodule Tagger.BookmarkTest do
  use ExUnit.Case

  alias Puka.Bookmarks.Bookmark
  alias Puka.Tags.Tag
  alias Puka.Repo
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

    bookmark =
      %Bookmark{}
      |> Bookmark.changeset(params)
      |> Repo.insert!()
      |> Repo.preload(:tags)

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

    bookmark =
      %Bookmark{}
      |> Bookmark.changeset(params)
      |> Repo.insert!()
      |> Repo.preload(:tags)

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

    bookmark =
      %Bookmark{}
      |> Bookmark.changeset(params)
      |> Repo.insert!()
      |> Repo.preload(:tags)

    assert tag_names(bookmark) == ["elixir"]
    assert Repo.aggregate(Tag, :count, :id) == 1
  end

  test "replaces tags on update" do
    bookmark =
      %Bookmark{}
      |> Bookmark.changeset(%{
        "title" => "Replace",
        "url" => "https://example.com/replace",
        "tags" => "elixir, ecto"
      })
      |> Repo.insert!()

    bookmark = Repo.preload(bookmark, :tags)

    bookmark =
      bookmark
      |> Bookmark.changeset(%{"tags" => "phoenix"})
      |> Repo.update!()
      |> Repo.preload(:tags)

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
