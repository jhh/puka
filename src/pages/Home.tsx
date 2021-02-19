import { gql, useQuery } from "@apollo/client";
import Container from "@material-ui/core/Container";
import { useSearchParams } from "react-router-dom";
import BookmarkList from "../components/Bookmark/BookmarkList";
import Error from "../components/Shared/Error";
import Loading from "../components/Shared/Loading";
import { BookmarkData } from "../components/Shared/types";

type BookmarksVars = {
  offset?: number;
  limit?: number;
  search?: string;
  tags?: string[];
};

const Home = () => {
  const [searchParams] = useSearchParams({});
  const query = searchParams.get("q");
  const tags = searchParams.getAll("t");

  let variables: BookmarksVars = { offset: 0, limit: 50 };

  if (query) variables.search = query;
  if (tags.length > 0) variables.tags = tags;

  const { loading, error, data } = useQuery<BookmarkData, BookmarksVars>(
    BOOKMARKS_QUERY,
    { variables }
  );

  if (error) return <Error error={error} />;

  return (
    <Container>
      {loading ? <Loading /> : <></>}
      {data ? <BookmarkList bookmarks={data.bookmarks} /> : <></>}
    </Container>
  );
};

export default Home;

const BOOKMARKS_QUERY = gql`
  query($search: String, $tags: [String], $offset: Int, $limit: Int) {
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
