defmodule Puka.Paginator do
  import Ecto.Query

  alias Puka.Repo

  @moduledoc """
  Provides pagination functionality.

  Give `Paginator.page/3` a query with a list of entities, plus the number of
  items you'd like to have on each page and it gives you methods for accessing
  the items for each page.
  """

  defstruct [:has_next, :has_prev, :prev_page, :page, :next_page, :first, :last, :count, :list]

  def query(query, page, per_page: per_page) when is_binary(page) do
    query(query, String.to_integer(page), per_page: per_page)
  end

  def query(query, page, per_page: per_page) do
    offset_val = per_page * (page - 1)

    query
    |> limit(^per_page)
    |> offset(^offset_val)
    |> Repo.all()
  end

  def page(query, page, per_page: per_page) when is_binary(page) do
    page(query, String.to_integer(page), per_page: per_page)
  end

  def page(query, page, per_page: per_page) do
    count = Repo.aggregate(query, :count, :id)
    results = query(query, page, per_page: per_page)

    has_next = page * per_page < count
    has_prev = page > 1

    %__MODULE__{
      has_next: has_next,
      has_prev: has_prev,
      prev_page: if(has_prev, do: page - 1, else: nil),
      page: page,
      next_page: if(has_next, do: page + 1, else: nil),
      first: (page - 1) * per_page + 1,
      last: Enum.min([page * per_page, count]),
      count: count,
      list: results
    }
  end
end
