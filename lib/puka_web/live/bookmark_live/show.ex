defmodule PukaWeb.BookmarkLive.Show do
  use PukaWeb, :live_view

  alias Puka.Bookmarks

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash} current_scope={@current_scope}>
      <.header>
        Bookmark {@bookmark.id}
        <:subtitle>This is a bookmark record from your database.</:subtitle>
        <:actions>
          <.button navigate={~p"/bookmarks"}>
            <.icon name="hero-arrow-left" />
          </.button>
          <.button variant="primary" navigate={~p"/bookmarks/#{@bookmark}/edit?return_to=show"}>
            <.icon name="hero-pencil-square" /> Edit bookmark
          </.button>
        </:actions>
      </.header>

      <.list>
        <:item title="Title">{@bookmark.title}</:item>
        <:item title="Description">{@bookmark.description}</:item>
        <:item title="Url">{@bookmark.url}</:item>
        <:item title="Active">{@bookmark.active}</:item>
      </.list>
    </Layouts.app>
    """
  end

  @impl true
  def mount(%{"id" => id}, _session, socket) do
    {:ok,
     socket
     |> assign(:page_title, "Show Bookmark")
     |> assign(:bookmark, Bookmarks.get_bookmark!(id))}
  end
end
