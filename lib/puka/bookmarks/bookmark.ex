defmodule Puka.Bookmarks.Bookmark do
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
  def changeset(bookmark, attrs) do
    bookmark
    |> cast(attrs, [:title, :description, :url, :active])
    |> validate_required([:title, :url])
    |> unique_constraint(:url)
    |> Ecto.Changeset.put_assoc(:tags, Tag.parse_tags(attrs))
  end
end
