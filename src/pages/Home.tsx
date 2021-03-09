import { gql, useQuery } from "@apollo/client";
import Container from "@material-ui/core/Container";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import BookmarkList from "../components/Bookmark/BookmarkList";
import CreateBookmark from "../components/Bookmark/CreateBookmark";
import Error from "../components/Shared/Error";
import Loading from "../components/Shared/Loading";
import { Bookmarks, BookmarksVariables } from "../generated/Bookmarks";

const Home = () => {
  const [searchParams] = useSearchParams({});
  const query = searchParams.get("q");
  const tags = searchParams.getAll("t");

  useEffect(() => {
    console.debug({ query, tags });
  }, [query, JSON.stringify(tags)]);

  let variables: BookmarksVariables = { offset: 0, limit: 50 };

  if (query) variables.search = query;
  if (tags.length > 0) variables.tags = tags;

  const { loading, error, data, fetchMore } = useQuery<
    Bookmarks,
    BookmarksVariables
  >(BOOKMARKS_QUERY, { variables });

  if (error) return <Error error={error} />;

  return (
    <Container>
      {loading ? <Loading /> : <></>}
      {data ? (
        <BookmarkList bookmarks={data.bookmarks} fetchMore={fetchMore} />
      ) : (
        <></>
      )}
      <CreateBookmark />
    </Container>
  );
};

export default Home;

const BOOKMARKS_QUERY = gql`
  query Bookmarks($search: String, $tags: [String], $offset: Int, $limit: Int) {
    bookmarks(search: $search, tags: $tags, offset: $offset, limit: $limit) {
      id
      title
      description
      url
      tags
      createdAt
    }
  }
`;
