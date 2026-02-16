defmodule PukaWeb.BookmarkLive.Index do
  use PukaWeb, :live_view

  import PukaWeb.CustomComponents

  alias Puka.Bookmarks

  @impl true
  def mount(_params, _session, socket) do
    {:ok, socket}
  end

  @impl true
  def handle_params(params, _uri, socket) do
    page = params["page"]
    pagination = Bookmarks.list_bookmarks(:paged, page, 10)

    socket =
      socket
      |> assign(:page_title, "Listing Bookmarks")
      |> assign(:pagination, pagination)
      |> stream(:bookmarks, pagination.list, reset: true)

    {:noreply, socket}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash} current_scope={@current_scope}>
      <.header>
        Listing Bookmarks
        <:actions>
          <.button variant="primary" navigate={~p"/bookmarks/new"}>
            <.icon name="hero-plus" /> New Bookmark
          </.button>
        </:actions>
      </.header>
      <.bookmark_list bookmarks={@streams.bookmarks} />
      <.pagination_controls path="/bookmarks" pagination={@pagination} />
    </Layouts.app>
    """
  end

  def bookmark_list(assigns) do
    ~H"""
    <ul id="bookmarks" class="list" phx-update="stream">
      <li :for={{id, bookmark} <- @bookmarks} id={id} class="list-row">
        <div class="list-col-grow">
          <div class="text-base font-semibold">{bookmark.title}</div>
          <div class="text-sm opacity-60 w-full md:max-w-3xl">{bookmark.description}</div>
          <div><.tag_list tags={bookmark.tags} /></div>
          <div class="text-xs opacity-60">
            <.icon name="hero-cloud-mini" class="size-3 opacity-40" />
            {get_domain(bookmark.url)}
            <span class="text-lg mx-1">·</span> {format_month_year(bookmark.inserted_at)}
          </div>
        </div>
      </li>
    </ul>
    """
  end

  def tag_list(assigns) do
    ~H"""
    <span>
      <a :for={tag <- @tags} href="#" class="mr-1 text-sm link-info" tabindex="-1">
        <.icon name="hero-hashtag-mini" class="size-2.25" />{tag.name}
      </a>
    </span>
    """
  end

  @impl true
  def handle_event("delete", %{"id" => id}, socket) do
    bookmark = Bookmarks.get_bookmark!(id)
    {:ok, _} = Bookmarks.delete_bookmark(bookmark)

    {:noreply, stream_delete(socket, :bookmarks, bookmark)}
  end

  defp get_domain(url) do
    case URI.parse(url) do
      %URI{host: nil} -> nil
      %URI{host: host} -> host
    end
  end

  def format_month_year(%DateTime{} = dt) do
    month = Calendar.strftime(dt, "%b") |> String.downcase()
    year = Integer.to_string(dt.year)
    "#{month} #{year}"
  end
end
