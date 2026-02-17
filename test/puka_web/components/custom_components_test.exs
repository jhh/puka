defmodule PukaWeb.CustomComponentsTest do
  use PukaWeb.ConnCase, async: true

  import Phoenix.LiveViewTest

  alias Puka.Paginator

  describe "pagination_controls/1" do
    test "renders pagination info showing correct range and count" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      assert html =~ "Showing 1 - 10 of 50"
      assert html =~ "Page 1"
    end

    test "on first page, Previous button is disabled and Next is enabled" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      # Previous button should be a disabled span
      assert html =~
               ~s(<span class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-50 text-zinc-300">)

      assert html =~ ~s(href="/bookmarks?page=2)
      refute html =~ ~s(href="/bookmarks?page=1)
    end

    test "on last page, Next button is disabled and Previous is enabled" do
      pagination = %Paginator{
        has_next: false,
        has_prev: true,
        prev_page: 4,
        page: 5,
        next_page: nil,
        first: 41,
        last: 50,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      # Next button should be a disabled span
      assert html =~
               ~s(<span class="px-3 py-2 rounded-lg text-sm font-medium bg-zinc-50 text-zinc-300">)

      assert html =~ ~s(href="/bookmarks?page=4)
      refute html =~ ~s(href="/bookmarks?page=6)
    end

    test "on middle page, both Previous and Next buttons are enabled" do
      pagination = %Paginator{
        has_next: true,
        has_prev: true,
        prev_page: 2,
        page: 3,
        next_page: 4,
        first: 21,
        last: 30,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      assert html =~ ~s(href="/bookmarks?page=2)
      assert html =~ ~s(href="/bookmarks?page=4)
    end

    test "includes tag query parameter in pagination links when present" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{"tag" => "elixir"}
        )

      assert html =~ ~s(href="/bookmarks?page=2&amp;tag=elixir)
    end

    test "excludes non-tag query parameters from pagination links" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{"tag" => "elixir", "sort" => "date", "filter" => "active"}
        )

      assert html =~ ~s(href="/bookmarks?page=2&amp;tag=elixir)
      refute html =~ ~s(sort=date)
      refute html =~ ~s(filter=active)
    end

    test "handles empty string tag value by excluding it from links" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{"tag" => ""}
        )

      assert html =~ ~s(href="/bookmarks?page=2)
      refute html =~ ~s(tag=)
    end

    test "handles nil tag value by excluding it from links" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{"tag" => nil}
        )

      assert html =~ ~s(href="/bookmarks?page=2)
    end

    test "handles empty params map" do
      pagination = %Paginator{
        has_next: true,
        has_prev: true,
        prev_page: 1,
        page: 2,
        next_page: 3,
        first: 11,
        last: 20,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      assert html =~ ~s(href="/bookmarks?page=1)
      assert html =~ ~s(href="/bookmarks?page=3)
    end

    test "handles special characters in tag value by HTML escaping" do
      pagination = %Paginator{
        has_next: true,
        has_prev: false,
        prev_page: nil,
        page: 1,
        next_page: 2,
        first: 1,
        last: 10,
        count: 50,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{"tag" => "elixir & phoenix"}
        )

      # Special characters are HTML-escaped in the rendered output
      assert html =~ ~s(href="/bookmarks?page=2&amp;tag=elixir &amp; phoenix)
    end

    test "correctly calculates pagination range for large datasets" do
      pagination = %Paginator{
        has_next: true,
        has_prev: true,
        prev_page: 9,
        page: 10,
        next_page: 11,
        first: 91,
        last: 100,
        count: 250,
        list: []
      }

      html =
        render_component(&PukaWeb.CustomComponents.pagination_controls/1,
          pagination: pagination,
          path: "/bookmarks",
          params: %{}
        )

      assert html =~ "Showing 91 - 100 of 250"
      assert html =~ "Page 10"
      assert html =~ ~s(href="/bookmarks?page=9)
      assert html =~ ~s(href="/bookmarks?page=11)
    end
  end
end
