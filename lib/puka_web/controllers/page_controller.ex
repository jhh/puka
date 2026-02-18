defmodule PukaWeb.PageController do
  use PukaWeb, :controller

  alias Puka.Bookmarks
  alias Puka.Tags

  def home(conn, _params) do
    bookmark_count = Bookmarks.count_bookmarks()
    tag_count = Tags.count_tags()
    render(conn, :home, bookmark_count: bookmark_count, tag_count: tag_count)
  end
end
