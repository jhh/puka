defmodule PukaWeb.TagLive.Show do
  use PukaWeb, :live_view

  alias Puka.Tags

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash}>
      <.header>
        Tag {@tag.id}
        <:subtitle>This is a tag record from your database.</:subtitle>
        <:actions>
          <.button navigate={~p"/tags"}>
            <.icon name="hero-arrow-left" />
          </.button>
          <.button variant="primary" navigate={~p"/tags/#{@tag}/edit?return_to=show"}>
            <.icon name="hero-pencil-square" /> Edit tag
          </.button>
        </:actions>
      </.header>

      <.list>
        <:item title="Name">{@tag.name}</:item>
      </.list>
    </Layouts.app>
    """
  end

  @impl true
  def mount(%{"id" => id}, _session, socket) do
    {:ok,
     socket
     |> assign(:page_title, "Show Tag")
     |> assign(:tag, Tags.get_tag!(id))}
  end
end
