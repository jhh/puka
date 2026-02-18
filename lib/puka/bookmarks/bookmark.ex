defmodule Puka.Bookmarks.Bookmark do
  @moduledoc """
  Bookmark schema.
  """
  use Ecto.Schema
  import Ecto.Changeset
  alias Puka.Tags.Tag

  schema "bookmarks" do
    field :title, :string
    field :description, :string
    field :url, :string
    field :active, :boolean, default: true

    many_to_many :tags, Tag,
      join_through: "bookmarks_tags",
      on_replace: :delete

    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(bookmark, attrs, opts \\ []) do
    bookmark
    |> cast(attrs, [:title, :description, :url, :active])
    |> validate_required([:title, :url])
    |> unique_constraint(:url)
    |> maybe_put_tags_assoc(attrs, opts)
  end

  defp maybe_put_tags_assoc(changeset, attrs, opts) do
    if Keyword.get(opts, :skip_tag_parse, false) do
      changeset
    else
      Ecto.Changeset.put_assoc(changeset, :tags, Tag.parse_tags(attrs))
    end
  end
end
