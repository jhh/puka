defmodule Puka.TagsFixtures do
  @moduledoc """
  This module defines test helpers for creating
  entities via the `Puka.Tags` context.
  """

  @doc """
  Generate a tag.
  """
  def tag_fixture(attrs \\ %{}) do
    {:ok, tag} =
      attrs
      |> Enum.into(%{
        name: "some name #{System.unique_integer([:positive])}"
      })
      |> Puka.Tags.create_tag()

    tag
  end
end
