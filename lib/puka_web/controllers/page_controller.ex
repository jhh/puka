defmodule PukaWeb.PageController do
  use PukaWeb, :controller

  def home(conn, _params) do
    render(conn, :home)
  end
end
