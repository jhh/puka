defmodule PukaWeb.BookmarkLive.Index do
  use PukaWeb, :live_view

  alias Puka.Bookmarks

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

      <.table
        id="bookmarks"
        rows={@streams.bookmarks}
      >
        <:col :let={{_id, bookmark}} label="Title">
          <.link href={bookmark.url} target="_blank" rel="noreferrer">{bookmark.title}</.link>
        </:col>
        <:col :let={{_id, bookmark}} label="Description">{bookmark.description}</:col>
        <:col :let={{_id, bookmark}} label="Url">{bookmark.url}</:col>
        <:col :let={{_id, bookmark}} label="Active">{bookmark.active}</:col>
        <:action :let={{_id, bookmark}}>
          <div class="sr-only">
            <.link navigate={~p"/bookmarks/#{bookmark}"}>Show</.link>
          </div>
          <.link navigate={~p"/bookmarks/#{bookmark}/edit"}>Edit</.link>
        </:action>
        <:action :let={{id, bookmark}}>
          <.link
            phx-click={JS.push("delete", value: %{id: bookmark.id}) |> hide("##{id}")}
            data-confirm="Are you sure?"
          >
            Delete
          </.link>
        </:action>
      </.table>
    </Layouts.app>
    """
  end

  @impl true
  def mount(_params, _session, socket) do
    {:ok,
     socket
     |> assign(:page_title, "Listing Bookmarks")
     |> stream(:bookmarks, list_bookmarks())}
  end

  @impl true
  def handle_event("delete", %{"id" => id}, socket) do
    bookmark = Bookmarks.get_bookmark!(id)
    {:ok, _} = Bookmarks.delete_bookmark(bookmark)

    {:noreply, stream_delete(socket, :bookmarks, bookmark)}
  end

  defp list_bookmarks() do
    Bookmarks.list_bookmarks()
  end
end
