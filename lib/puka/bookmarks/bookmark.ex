defmodule Puka.Bookmarks.Bookmark do
  @moduledoc """
  Bookmark schema.
  """
  use Ecto.Schema
  import Ecto.Changeset

  schema "bookmarks" do
    field :title, :string
    field :description, :string
    field :url, :string
    field :active, :boolean, default: true

    many_to_many :tags, Puka.Tags.Tag,
      join_through: "bookmarks_tags",
      on_replace: :delete

    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(bookmark, attrs, tags \\ :skip) do
    changeset =
      bookmark
      |> cast(attrs, [:title, :description, :url, :active])
      |> validate_required([:title, :url])
      |> unique_constraint(:url)

    if tags == :skip do
      changeset
    else
      put_assoc(changeset, :tags, tags)
    end
  end
end
