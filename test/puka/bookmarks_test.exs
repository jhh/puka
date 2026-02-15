defmodule Puka.BookmarksTest do
  use Puka.DataCase

  alias Puka.Bookmarks

  describe "bookmarks" do
    alias Puka.Bookmarks.Bookmark

    import Puka.BookmarksFixtures

    @invalid_attrs %{active: nil, description: nil, title: nil, url: nil}

    test "list_bookmarks/0 returns all bookmarks" do
      bookmark = bookmark_fixture()
      assert Bookmarks.list_bookmarks() == [bookmark]
    end

    test "get_bookmark!/1 returns the bookmark with given id" do
      bookmark = bookmark_fixture()
      assert Bookmarks.get_bookmark!(bookmark.id) == bookmark
    end

    test "create_bookmark/1 with valid data creates a bookmark" do
      valid_attrs = %{
        active: true,
        description: "some description",
        title: "some title",
        url: "some url"
      }

      assert {:ok, %Bookmark{} = bookmark} = Bookmarks.create_bookmark(valid_attrs)
      assert bookmark.active == true
      assert bookmark.description == "some description"
      assert bookmark.title == "some title"
      assert bookmark.url == "some url"
    end

    test "create_bookmark/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Bookmarks.create_bookmark(@invalid_attrs)
    end

    test "update_bookmark/2 with valid data updates the bookmark" do
      bookmark = bookmark_fixture()

      update_attrs = %{
        active: false,
        description: "some updated description",
        title: "some updated title",
        url: "some updated url"
      }

      assert {:ok, %Bookmark{} = bookmark} = Bookmarks.update_bookmark(bookmark, update_attrs)
      assert bookmark.active == false
      assert bookmark.description == "some updated description"
      assert bookmark.title == "some updated title"
      assert bookmark.url == "some updated url"
    end

    test "update_bookmark/2 with invalid data returns error changeset" do
      bookmark = bookmark_fixture()
      assert {:error, %Ecto.Changeset{}} = Bookmarks.update_bookmark(bookmark, @invalid_attrs)
      assert bookmark == Bookmarks.get_bookmark!(bookmark.id)
    end

    test "delete_bookmark/1 deletes the bookmark" do
      bookmark = bookmark_fixture()
      assert {:ok, %Bookmark{}} = Bookmarks.delete_bookmark(bookmark)
      assert_raise Ecto.NoResultsError, fn -> Bookmarks.get_bookmark!(bookmark.id) end
    end

    test "change_bookmark/1 returns a bookmark changeset" do
      bookmark = bookmark_fixture()
      assert %Ecto.Changeset{} = Bookmarks.change_bookmark(bookmark)
    end
  end

  describe "list_bookmarks/3 with :paged" do
    import Puka.BookmarksFixtures

    test "returns paginated results with correct structure" do
      bookmark = bookmark_fixture()
      result = Bookmarks.list_bookmarks(:paged, 1, 10)

      assert result.page == 1
      assert result.count == 1
      assert result.has_next == false
      assert result.has_prev == false
      assert result.prev_page == nil
      assert result.next_page == nil
      assert result.first == 1
      assert result.last == 1
      assert length(result.list) == 1
      assert hd(result.list).id == bookmark.id
    end

    test "returns correct pagination for multiple pages" do
      for i <- 1..25 do
        bookmark_fixture(%{url: "https://example#{i}.com", title: "Bookmark #{i}"})
      end

      result = Bookmarks.list_bookmarks(:paged, 1, 10)

      assert result.page == 1
      assert result.count == 25
      assert result.has_next == true
      assert result.has_prev == false
      assert result.prev_page == nil
      assert result.next_page == 2
      assert result.first == 1
      assert result.last == 10
      assert length(result.list) == 10

      result = Bookmarks.list_bookmarks(:paged, 2, 10)

      assert result.page == 2
      assert result.has_next == true
      assert result.has_prev == true
      assert result.prev_page == 1
      assert result.next_page == 3
      assert result.first == 11
      assert result.last == 20
      assert length(result.list) == 10

      result = Bookmarks.list_bookmarks(:paged, 3, 10)

      assert result.page == 3
      assert result.has_next == false
      assert result.has_prev == true
      assert result.prev_page == 2
      assert result.next_page == nil
      assert result.first == 21
      assert result.last == 25
      assert length(result.list) == 5
    end

    test "respects per_page parameter" do
      for i <- 1..8 do
        bookmark_fixture(%{url: "https://example#{i}.com", title: "Bookmark #{i}"})
      end

      result = Bookmarks.list_bookmarks(:paged, 1, 3)

      assert result.count == 8
      assert result.has_next == true
      assert length(result.list) == 3

      result = Bookmarks.list_bookmarks(:paged, 3, 3)

      assert result.has_next == false
      assert length(result.list) == 2
    end

    test "returns empty list for page beyond results" do
      bookmark_fixture()

      result = Bookmarks.list_bookmarks(:paged, 5, 10)

      assert result.count == 1
      assert result.has_next == false
      assert result.has_prev == true
      assert length(result.list) == 0
    end

    test "preloads tags for each bookmark" do
      bookmark = bookmark_fixture(%{tags: "elixir, phoenix"})

      result = Bookmarks.list_bookmarks(:paged, 1, 10)

      assert length(result.list) == 1
      loaded_bookmark = hd(result.list)
      assert loaded_bookmark.id == bookmark.id
      assert length(loaded_bookmark.tags) == 2
      tag_names = Enum.map(loaded_bookmark.tags, & &1.name) |> Enum.sort()
      assert tag_names == ["elixir", "phoenix"]
    end

    @tag :slow
    test "orders bookmarks by inserted_at descending" do
      bookmark1 = bookmark_fixture(%{url: "https://example1.com", title: "First"})
      :timer.sleep(1100)
      bookmark2 = bookmark_fixture(%{url: "https://example2.com", title: "Second"})

      result = Bookmarks.list_bookmarks(:paged, 1, 10)

      assert hd(result.list).id == bookmark2.id
      assert Enum.at(result.list, 1).id == bookmark1.id
    end

    test "handles string page number" do
      bookmark_fixture()

      result = Bookmarks.list_bookmarks(:paged, "1", 10)

      assert result.page == 1
    end
  end
end
