defmodule PukaWeb.BookmarkLiveTest do
  use PukaWeb.ConnCase

  import Phoenix.LiveViewTest
  import Puka.BookmarksFixtures

  alias Puka.Repo
  alias Puka.Tags.Tag

  setup :register_and_log_in_user

  @create_attrs %{
    active: true,
    description: "some description",
    title: "some title",
    url: "some url"
  }
  @update_attrs %{
    active: false,
    description: "some updated description",
    title: "some updated title",
    url: "some updated url"
  }
  @invalid_attrs %{active: false, description: nil, title: nil, url: nil}
  defp create_bookmark(_) do
    bookmark = bookmark_fixture()

    %{bookmark: bookmark}
  end

  describe "Index" do
    setup [:create_bookmark]

    test "lists all bookmarks", %{conn: conn, bookmark: bookmark} do
      {:ok, _index_live, html} = live(conn, ~p"/bookmarks")

      assert html =~ "Listing Bookmarks"
      assert html =~ bookmark.title
    end

    test "saves new bookmark", %{conn: conn} do
      {:ok, index_live, _html} = live(conn, ~p"/bookmarks")

      assert {:ok, form_live, _} =
               index_live
               |> element("a", "New Bookmark")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/new")

      assert render(form_live) =~ "New Bookmark"

      assert form_live
             |> form("#bookmark-form", bookmark: @invalid_attrs)
             |> render_change() =~ "can&#39;t be blank"

      assert {:ok, index_live, _html} =
               form_live
               |> form("#bookmark-form", bookmark: @create_attrs)
               |> render_submit()
               |> follow_redirect(conn, ~p"/bookmarks")

      html = render(index_live)
      assert html =~ "Bookmark created successfully"
      assert html =~ "some title"
    end

    test "saves new bookmark with tags", %{conn: conn} do
      {:ok, index_live, _html} = live(conn, ~p"/bookmarks")

      assert {:ok, form_live, _} =
               index_live
               |> element("a", "New Bookmark")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/new")

      assert has_element?(form_live, "#bookmark-tags")

      create_attrs =
        @create_attrs
        |> Map.put(:tags, "FreshOne, FreshTwo")
        |> Map.put(:url, "https://fresh-tags.example")

      assert {:ok, index_live, _html} =
               form_live
               |> form("#bookmark-form", bookmark: create_attrs)
               |> render_submit()
               |> follow_redirect(conn, ~p"/bookmarks")

      assert has_element?(index_live, "a.link-info", "freshone")
      assert has_element?(index_live, "a.link-info", "freshtwo")
    end

    test "renders tags input without creating tags on change", %{conn: conn} do
      {:ok, index_live, _html} = live(conn, ~p"/bookmarks")

      assert {:ok, form_live, _} =
               index_live
               |> element("a", "New Bookmark")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/new")

      assert has_element?(form_live, "#bookmark-tags")

      tag_count = Repo.aggregate(Tag, :count, :id)

      form_live
      |> form("#bookmark-form", bookmark: Map.put(@create_attrs, :tags, "elixir, phoenix"))
      |> render_change()

      assert Repo.aggregate(Tag, :count, :id) == tag_count
    end

    test "updates bookmark in listing", %{conn: conn, bookmark: bookmark} do
      {:ok, index_live, _html} = live(conn, ~p"/bookmarks")

      assert {:ok, form_live, _html} =
               index_live
               |> element("#bookmarks-#{bookmark.id} a", "Edit")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/#{bookmark}/edit")

      assert render(form_live) =~ "Edit Bookmark"

      assert has_element?(form_live, "#bookmark-tags")

      assert form_live
             |> form("#bookmark-form", bookmark: @invalid_attrs)
             |> render_change() =~ "can&#39;t be blank"

      assert {:ok, index_live, _html} =
               form_live
               |> form("#bookmark-form", bookmark: @update_attrs)
               |> render_submit()
               |> follow_redirect(conn, ~p"/bookmarks")

      html = render(index_live)
      assert html =~ "Bookmark updated successfully"
      assert html =~ "some updated title"
    end

    test "updates bookmark tags", %{conn: conn, bookmark: bookmark} do
      {:ok, index_live, _html} = live(conn, ~p"/bookmarks")

      assert {:ok, form_live, _html} =
               index_live
               |> element("#bookmarks-#{bookmark.id} a", "Edit")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/#{bookmark}/edit")

      update_attrs =
        @update_attrs
        |> Map.put(:tags, "UpdatedOne, UpdatedTwo")
        |> Map.put(:url, "https://updated-tags.example")

      assert {:ok, index_live, _html} =
               form_live
               |> form("#bookmark-form", bookmark: update_attrs)
               |> render_submit()
               |> follow_redirect(conn, ~p"/bookmarks")

      assert has_element?(index_live, "a.link-info", "updatedone")
      assert has_element?(index_live, "a.link-info", "updatedtwo")
    end
  end

  describe "Show" do
    setup [:create_bookmark]

    test "displays bookmark", %{conn: conn, bookmark: bookmark} do
      {:ok, _show_live, html} = live(conn, ~p"/bookmarks/#{bookmark}")

      assert html =~ "Show Bookmark"
      assert html =~ bookmark.title
    end

    test "updates bookmark and returns to show", %{conn: conn, bookmark: bookmark} do
      {:ok, show_live, _html} = live(conn, ~p"/bookmarks/#{bookmark}")

      assert {:ok, form_live, _} =
               show_live
               |> element("a", "Edit")
               |> render_click()
               |> follow_redirect(conn, ~p"/bookmarks/#{bookmark}/edit?return_to=show")

      assert render(form_live) =~ "Edit Bookmark"

      assert form_live
             |> form("#bookmark-form", bookmark: @invalid_attrs)
             |> render_change() =~ "can&#39;t be blank"

      assert {:ok, show_live, _html} =
               form_live
               |> form("#bookmark-form", bookmark: @update_attrs)
               |> render_submit()
               |> follow_redirect(conn, ~p"/bookmarks/#{bookmark}")

      html = render(show_live)
      assert html =~ "Bookmark updated successfully"
      assert html =~ "some updated title"
    end
  end
end
