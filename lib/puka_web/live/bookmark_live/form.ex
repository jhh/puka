defmodule PukaWeb.BookmarkLive.Form do
  use PukaWeb, :live_view

  alias Puka.Bookmarks
  alias Puka.Bookmarks.Bookmark

  @impl true
  def render(assigns) do
    ~H"""
    <Layouts.app flash={@flash} current_scope={@current_scope}>
      <.header>
        {@page_title}
        <:subtitle>Use this form to manage bookmark records in your database.</:subtitle>
      </.header>

      <.form for={@form} id="bookmark-form" phx-change="validate" phx-submit="save">
        <.input field={@form[:title]} type="text" label="Title" />
        <.input field={@form[:description]} type="textarea" label="Description" />
        <.input field={@form[:url]} type="text" label="Url" />
        <.input
          id="bookmark-tags"
          name="bookmark[tags]"
          type="text"
          label="Tags"
          value={Map.get(@form.params || %{}, "tags", "")}
          placeholder="elixir, phoenix"
        />
        <.input field={@form[:active]} type="checkbox" label="Active" />
        <footer>
          <.button phx-disable-with="Saving..." variant="primary">Save Bookmark</.button>
          <.button navigate={return_path(@return_to, @bookmark)}>Cancel</.button>
        </footer>
      </.form>
    </Layouts.app>
    """
  end

  @impl true
  def mount(params, _session, socket) do
    {:ok,
     socket
     |> assign(:return_to, return_to(params["return_to"]))
     |> apply_action(socket.assigns.live_action, params)}
  end

  defp return_to("show"), do: "show"
  defp return_to(_), do: "index"

  defp apply_action(socket, :edit, %{"id" => id}) do
    bookmark = Bookmarks.get_bookmark!(id)

    socket
    |> assign(:page_title, "Edit Bookmark")
    |> assign(:bookmark, bookmark)
    |> assign(:form, to_form(Bookmarks.change_bookmark(bookmark)))
  end

  defp apply_action(socket, :new, _params) do
    bookmark = %Bookmark{}

    socket
    |> assign(:page_title, "New Bookmark")
    |> assign(:bookmark, bookmark)
    |> assign(:form, to_form(Bookmarks.change_bookmark(bookmark)))
  end

  @impl true
  def handle_event("validate", %{"bookmark" => bookmark_params}, socket) do
    changeset =
      Bookmarks.change_bookmark(socket.assigns.bookmark, bookmark_params)

    {:noreply, assign(socket, form: to_form(changeset, action: :validate))}
  end

  def handle_event("save", %{"bookmark" => bookmark_params}, socket) do
    save_bookmark(socket, socket.assigns.live_action, bookmark_params)
  end

  defp save_bookmark(socket, :edit, bookmark_params) do
    case Bookmarks.update_bookmark(socket.assigns.bookmark, bookmark_params) do
      {:ok, bookmark} ->
        {:noreply,
         socket
         |> put_flash(:info, "Bookmark updated successfully")
         |> push_navigate(to: return_path(socket.assigns.return_to, bookmark))}

      {:error, %Ecto.Changeset{} = changeset} ->
        {:noreply, assign(socket, form: to_form(changeset))}
    end
  end

  defp save_bookmark(socket, :new, bookmark_params) do
    case Bookmarks.create_bookmark(bookmark_params) do
      {:ok, bookmark} ->
        {:noreply,
         socket
         |> put_flash(:info, "Bookmark created successfully")
         |> push_navigate(to: return_path(socket.assigns.return_to, bookmark))}

      {:error, %Ecto.Changeset{} = changeset} ->
        {:noreply, assign(socket, form: to_form(changeset))}
    end
  end

  defp return_path("index", _bookmark), do: ~p"/bookmarks"
  defp return_path("show", bookmark), do: ~p"/bookmarks/#{bookmark}"
end
