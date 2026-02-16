defmodule PukaWeb.CustomComponents do
  use PukaWeb, :html

  attr :pagination, Puka.Paginator, required: true
  attr :path, :string, required: true

  def pagination_controls(assigns) do
    ~H"""
    <div class="flex items-center justify-between mt-4">
      <div class="text-sm text-zinc-500">
        Showing {@pagination.first} - {@pagination.last} of {@pagination.count}
      </div>
      <div class="flex items-center gap-2">
        <%= if @pagination.has_prev do %>
          <.link
            patch={"#{@path}?page=#{@pagination.prev_page}"}
            class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition-colors"
          >
            <.icon name="hero-chevron-left" /> Previous
          </.link>
        <% else %>
          <span class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-50 text-zinc-300">
            <.icon name="hero-chevron-left" /> Previous
          </span>
        <% end %>
        <span class="px-3 py-2 text-sm text-zinc-600">
          Page {@pagination.page}
        </span>
        <%= if @pagination.has_next do %>
          <.link
            patch={"#{@path}?page=#{@pagination.next_page}"}
            class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition-colors"
          >
            Next <.icon name="hero-chevron-right" />
          </.link>
        <% else %>
          <span class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-50 text-zinc-300">
            Next <.icon name="hero-chevron-right" />
          </span>
        <% end %>
      </div>
    </div>
    """
  end
end
