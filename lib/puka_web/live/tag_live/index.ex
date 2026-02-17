defmodule PukaWeb.TagLive.Index do
  use PukaWeb, :live_view

  import PukaWeb.CustomComponents

  alias Puka.Tags

  @impl true
  def mount(_params, _session, socket) do
    {:ok, socket}
  end

  @impl true
  def handle_params(params, _uri, socket) do
    page = params["page"]
    pagination = Tags.list_tags(:paged, page)

    socket =
      socket
      |> assign(:page_title, "Listing Tags")
      |> assign(:pagination, pagination)
      |> assign(:current_params, params)
      |> stream(:tags, pagination.list, reset: true)

    {:noreply, socket}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash} current_scope={@current_scope}>
      <.header>
        Listing Tags
        <:actions>
          <.button variant="primary" navigate={~p"/tags/new"}>
            <.icon name="hero-plus" /> New Tag
          </.button>
        </:actions>
      </.header>

      <.table
        id="tags"
        rows={@streams.tags}
        row_click={fn {_id, tag} -> JS.navigate(~p"/tags/#{tag}") end}
      >
        <:col :let={{_id, tag}} label="Name">{tag.name}</:col>
        <:action :let={{_id, tag}}>
          <div class="sr-only">
            <.link navigate={~p"/tags/#{tag}"}>Show</.link>
          </div>
          <.link navigate={~p"/tags/#{tag}/edit"}>Edit</.link>
        </:action>
        <:action :let={{id, tag}}>
          <.link
            phx-click={JS.push("delete", value: %{id: tag.id}) |> hide("##{id}")}
            data-confirm="Are you sure?"
          >
            Delete
          </.link>
        </:action>
      </.table>
      <.pagination_controls path="/tags" pagination={@pagination} params={@current_params} />
    </Layouts.app>
    """
  end

  @impl true
  def handle_event("delete", %{"id" => id}, socket) do
    tag = Tags.get_tag!(id)
    {:ok, _} = Tags.delete_tag(tag)

    {:noreply, stream_delete(socket, :tags, tag)}
  end
end
