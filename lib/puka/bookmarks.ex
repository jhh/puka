defmodule Puka.Bookmarks do
  @moduledoc """
  The Bookmarks context.
  """

  import Ecto.Query, warn: false
  alias Puka.{Paginator, Repo}

  alias Puka.Bookmarks.Bookmark

  @page_size 10

  @doc """
  Returns the list of bookmarks with tags preloaded.

  ## Examples

      iex> list_bookmarks()
      [%Bookmark{}, ...]

  """
  def list_bookmarks do
    Bookmark |> order_by(desc: :inserted_at) |> Repo.all() |> Repo.preload(:tags)
  end

  def list_bookmarks(a, page \\ 1, per_page \\ @page_size)

  def list_bookmarks(:paged, page, per_page) do
    Bookmark
    |> order_by(desc: :inserted_at)
    |> preload(:tags)
    |> Paginator.page(page, per_page: per_page)
  end

  @doc """
  Gets a single bookmark with its tags preloaded.

  Raises `Ecto.NoResultsError` if the Bookmark does not exist.

  ## Examples

      iex> get_bookmark!(123)
      %Bookmark{}

      iex> get_bookmark!(456)
      ** (Ecto.NoResultsError)

  """
  def get_bookmark!(id), do: Repo.get!(Bookmark, id) |> Repo.preload(:tags)

  @doc """
  Creates a bookmark. In addition to `Bookmark` schema fields, `attrs` can
  contain a field for related tags: `"tags" => "tag1, tag2, tag2"`. Tags in this
  list are created as neccessary.

  ## Examples

      iex> create_bookmark(%{field: value})
      {:ok, %Bookmark{}}

      iex> create_bookmark(%{field: bad_value})
      {:error, %Ecto.Changeset{}}

  """
  def create_bookmark(attrs) do
    %Bookmark{}
    |> Bookmark.changeset(attrs)
    |> Repo.insert()
  end

  @doc """
  Updates a bookmark.

  ## Examples

      iex> update_bookmark(bookmark, %{field: new_value})
      {:ok, %Bookmark{}}

      iex> update_bookmark(bookmark, %{field: bad_value})
      {:error, %Ecto.Changeset{}}

  """
  def update_bookmark(%Bookmark{} = bookmark, attrs) do
    bookmark
    |> Bookmark.changeset(attrs)
    |> Repo.update()
  end

  @doc """
  Deletes a bookmark.

  ## Examples

      iex> delete_bookmark(bookmark)
      {:ok, %Bookmark{}}

      iex> delete_bookmark(bookmark)
      {:error, %Ecto.Changeset{}}

  """
  def delete_bookmark(%Bookmark{} = bookmark) do
    Repo.delete(bookmark)
  end

  @doc """
  Returns an `%Ecto.Changeset{}` for tracking bookmark changes.

  ## Examples

      iex> change_bookmark(bookmark)
      %Ecto.Changeset{data: %Bookmark{}}

  """
  def change_bookmark(%Bookmark{} = bookmark, attrs \\ %{}) do
    Bookmark.changeset(bookmark, attrs)
  end
end

# iex(11)> query = from b in Bookmark,
# ...(11)>   join: t in assoc(b, :tags),
# ...(11)>   where: t.name == "elixir",
# ...(11)>   preload: [:tags]
