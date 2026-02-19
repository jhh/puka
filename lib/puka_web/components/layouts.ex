defmodule PukaWeb.Layouts do
  @moduledoc """
  This module holds layouts and related functionality
  used by your application.
  """
  use PukaWeb, :html
  alias Puka.Accounts.Scope

  # Embed all files in layouts/* within this module.
  # The default root.html.heex file contains the HTML
  # skeleton of your application, namely HTML headers
  # and other static content.
  embed_templates "layouts/*"

  @doc """
  Renders your app layout.

  This function is typically invoked from every template,
  and it often contains your application menu, sidebar,
  or similar.

  ## Examples

      <Layouts.app flash={@flash}>
        <h1>Content</h1>
      </Layouts.app>

  """
  attr :flash, :map, required: true, doc: "the map of flash messages"

  attr :current_scope, :map,
    default: nil,
    doc: "the current [scope](https://hexdocs.pm/phoenix/scopes.html)"

  slot :inner_block, required: true

  def app(assigns) do
    ~H"""
    <div class="drawer lg:drawer-open">
      <input id="app-drawer" type="checkbox" class="drawer-toggle" />

      <div class="drawer-content bg-base-100">
        <header class="navbar sticky top-0 z-20 border-b border-base-200 bg-base-100/90 px-4 backdrop-blur sm:px-6 lg:px-8">
          <div class="navbar-start gap-2">
            <label
              for="app-drawer"
              aria-label="open sidebar"
              class="btn btn-square btn-ghost lg:hidden"
            >
              <.icon name="hero-bars-3" class="size-5" />
            </label>
          </div>

          <div class="navbar-end gap-2">
            <details class="dropdown dropdown-end">
              <summary class="btn btn-ghost gap-2 px-2">
                <%= if user_email(@current_scope) do %>
                  <div class="hidden text-sm font-medium text-base-content/80 sm:block">
                    {user_email(@current_scope)}
                  </div>
                <% end %>

                <.icon name="hero-chevron-down" class="size-4 text-base-content/60" />
              </summary>

              <ul class="menu dropdown-content z-30 mt-2 w-56 rounded-box border border-base-200 bg-base-100 p-2 shadow">
                <%= if @current_scope do %>
                  <li class="menu-title">
                    <span>Account</span>
                  </li>
                  <li>
                    <div class="flex items-center justify-between">
                      <span class="text-xs text-base-content/60">Theme</span>
                      <.theme_toggle />
                    </div>
                  </li>
                  <li>
                    <.link href={~p"/users/settings"}>
                      <.icon name="hero-cog-6-tooth" class="size-4" /> Settings
                    </.link>
                  </li>
                  <li>
                    <.link href={~p"/users/log-out"} method="delete">
                      <.icon name="hero-arrow-left-on-rectangle" class="size-4" /> Log out
                    </.link>
                  </li>
                <% else %>
                  <li>
                    <.link href={~p"/users/register"}>
                      <.icon name="hero-user-plus" class="size-4" /> Register
                    </.link>
                  </li>
                  <li>
                    <.link href={~p"/users/log-in"}>
                      <.icon name="hero-arrow-right-on-rectangle" class="size-4" /> Log in
                    </.link>
                  </li>
                <% end %>
              </ul>
            </details>
          </div>
        </header>

        <main class="min-h-[calc(100vh-4rem)] bg-base-100 px-4 py-6 sm:px-6 lg:px-8">
          <div class="mx-auto w-full max-w-screen-2xl">
            {render_slot(@inner_block)}
          </div>
        </main>

        <.flash_group flash={@flash} />
      </div>

      <div class="drawer-side z-30 is-drawer-close:overflow-visible">
        <label for="app-drawer" aria-label="close sidebar" class="drawer-overlay"></label>

        <aside class="flex min-h-full flex-col border-r border-base-200 bg-base-200 is-drawer-close:w-14 is-drawer-open:w-72">
          <div class="flex h-16 items-center border-b border-base-200/60 px-4">
            <a href={~p"/"} class="is-drawer-close:hidden">
              <img src={~p"/images/puka-logo.svg"} class="w-[180px] max-w-full h-auto" alt="Puka" />
            </a>
          </div>

          <ul class="menu menu-md w-full grow px-2">
            <li class="menu-title is-drawer-close:hidden"><span>Manage</span></li>
            <li>
              <.link
                href={~p"/"}
                class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                data-tip="Overview"
              >
                <.icon name="hero-home" class="size-4" />
                <span class="is-drawer-close:hidden">Overview</span>
              </.link>
            </li>

            <%= if @current_scope do %>
              <li class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Bookmarks">
                <details open>
                  <summary class="is-drawer-close:hidden">
                    <.icon name="hero-bookmark" class="size-4" /> Bookmarks
                  </summary>
                  <ul class="is-drawer-close:hidden">
                    <li>
                      <.link href={~p"/bookmarks"}>Browse</.link>
                    </li>
                    <li>
                      <.link href={~p"/bookmarks"}>Filter</.link>
                    </li>
                  </ul>
                </details>
                <.link href={~p"/bookmarks"} class="hidden is-drawer-close:flex">
                  <.icon name="hero-bookmark" class="size-4" />
                </.link>
              </li>
              <li>
                <.link
                  href={~p"/tags"}
                  class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                  data-tip="Tags"
                >
                  <.icon name="hero-tag" class="size-4" />
                  <span class="is-drawer-close:hidden">Tags</span>
                </.link>
              </li>
            <% else %>
              <li
                class="disabled is-drawer-close:tooltip is-drawer-close:tooltip-right"
                data-tip="Log in to use"
              >
                <details>
                  <summary class="is-drawer-close:hidden">
                    <.icon name="hero-bookmark" class="size-4" /> Bookmarks
                  </summary>
                  <ul class="is-drawer-close:hidden">
                    <li><a>Browse</a></li>
                    <li><a>Filter</a></li>
                  </ul>
                </details>
                <a class="hidden is-drawer-close:flex">
                  <.icon name="hero-bookmark" class="size-4" />
                </a>
              </li>
              <li class="disabled">
                <a
                  class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                  data-tip="Log in to use"
                >
                  <.icon name="hero-tag" class="size-4" />
                  <span class="is-drawer-close:hidden">Tags</span>
                </a>
              </li>
            <% end %>

            <li class="menu-title is-drawer-close:hidden"><span>Account</span></li>
            <%= if @current_scope do %>
              <li>
                <.link
                  href={~p"/users/settings"}
                  class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                  data-tip="Settings"
                >
                  <.icon name="hero-cog-6-tooth" class="size-4" />
                  <span class="is-drawer-close:hidden">Settings</span>
                </.link>
              </li>
            <% else %>
              <li>
                <.link
                  href={~p"/users/log-in"}
                  class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                  data-tip="Log in"
                >
                  <.icon name="hero-arrow-right-on-rectangle" class="size-4" />
                  <span class="is-drawer-close:hidden">Log in</span>
                </.link>
              </li>
            <% end %>
          </ul>
        </aside>
      </div>
    </div>
    """
  end

  defp user_email(nil), do: nil

  defp user_email(%Scope{user: %{email: email}}) when is_binary(email) and byte_size(email) > 0,
    do: email

  defp user_email(_), do: nil

  @doc """
  Shows the flash group with standard titles and content.

  ## Examples

      <.flash_group flash={@flash} />
  """
  attr :flash, :map, required: true, doc: "the map of flash messages"
  attr :id, :string, default: "flash-group", doc: "the optional id of flash container"

  def flash_group(assigns) do
    ~H"""
    <div id={@id} aria-live="polite">
      <.flash kind={:info} flash={@flash} />
      <.flash kind={:error} flash={@flash} />

      <.flash
        id="client-error"
        kind={:error}
        title={gettext("We can't find the internet")}
        phx-disconnected={show(".phx-client-error #client-error") |> JS.remove_attribute("hidden")}
        phx-connected={hide("#client-error") |> JS.set_attribute({"hidden", ""})}
        hidden
      >
        {gettext("Attempting to reconnect")}
        <.icon name="hero-arrow-path" class="ml-1 size-3 motion-safe:animate-spin" />
      </.flash>

      <.flash
        id="server-error"
        kind={:error}
        title={gettext("Something went wrong!")}
        phx-disconnected={show(".phx-server-error #server-error") |> JS.remove_attribute("hidden")}
        phx-connected={hide("#server-error") |> JS.set_attribute({"hidden", ""})}
        hidden
      >
        {gettext("Attempting to reconnect")}
        <.icon name="hero-arrow-path" class="ml-1 size-3 motion-safe:animate-spin" />
      </.flash>
    </div>
    """
  end

  @doc """
  Provides dark vs light theme toggle based on themes defined in app.css.

  See <head> in root.html.heex which applies the theme before page load.
  """
  def theme_toggle(assigns) do
    ~H"""
    <div class="card relative flex flex-row items-center border-2 border-base-300 bg-base-300 rounded-full">
      <div class="absolute w-1/3 h-full rounded-full border-1 border-base-200 bg-base-100 brightness-200 left-0 [[data-theme=light]_&]:left-1/3 [[data-theme=dark]_&]:left-2/3 transition-[left]" />

      <button
        class="flex p-2 cursor-pointer w-1/3"
        phx-click={JS.dispatch("phx:set-theme")}
        data-phx-theme="system"
      >
        <.icon name="hero-computer-desktop-micro" class="size-4 opacity-75 hover:opacity-100" />
      </button>

      <button
        class="flex p-2 cursor-pointer w-1/3"
        phx-click={JS.dispatch("phx:set-theme")}
        data-phx-theme="light"
      >
        <.icon name="hero-sun-micro" class="size-4 opacity-75 hover:opacity-100" />
      </button>

      <button
        class="flex p-2 cursor-pointer w-1/3"
        phx-click={JS.dispatch("phx:set-theme")}
        data-phx-theme="dark"
      >
        <.icon name="hero-moon-micro" class="size-4 opacity-75 hover:opacity-100" />
      </button>
    </div>
    """
  end
end
