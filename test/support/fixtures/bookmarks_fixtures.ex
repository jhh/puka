defmodule Puka.BookmarksFixtures do
  @moduledoc """
  This module defines test helpers for creating
  entities via the `Puka.Bookmarks` context.
  """

  @doc """
  Generate a bookmark.
  """
  def bookmark_fixture(attrs \\ %{}) do
    {:ok, bookmark} =
      attrs
      |> Enum.into(%{
        active: true,
        description: "some description",
        title: "some title",
        url: "https://example.com",
        tags: "one,two"
      })
      |> Puka.Bookmarks.create_bookmark()

    bookmark
  end
end
