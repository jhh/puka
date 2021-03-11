import { gql, useQuery } from "@apollo/client";
import InfiniteScroll from "react-infinite-scroll-component";
import { useSearchParams } from "react-router-dom";
import Error from "../../components/Shared/Error";
import Loading from "../../components/Shared/Loading";
import {
  AllBookmarks,
  AllBookmarksVariables,
} from "../../generated/AllBookmarks";
import Bookmarks from "./Bookmarks";

const BOOKMARKS_QUERY = gql`
  query AllBookmarks($search: String, $tags: String, $cursor: String) {
    allBookmarks(
      search: $search
      tags: $tags
      first: 50
      after: $cursor
      orderBy: "-created_at"
    ) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          id
          title
          description
          url
          tags
          createdAt
        }
      }
    }
  }
`;

const BookmarksWithData = () => {
  const [searchParams] = useSearchParams({});
  const query = searchParams.get("q");
  const tags = searchParams.getAll("t");

  let variables: AllBookmarksVariables = { search: "", tags: "" };
  if (query) variables.search = query;
  if (tags.length > 0) variables.tags = tags.join(",");

  const { loading, error, data, fetchMore } = useQuery<
    AllBookmarks,
    AllBookmarksVariables
  >(BOOKMARKS_QUERY, { variables });

  if (error) return <Error error={error} />;
  if (loading) return <Loading />;

  const edges = data?.allBookmarks?.edges || [];
  const nodes = edges.map((edge) => (edge ? edge.node : null));
  const pageInfo = data?.allBookmarks?.pageInfo;

  return (
    <InfiniteScroll
      dataLength={nodes.length}
      hasMore={!!pageInfo?.hasNextPage}
      loader={<h4>Loading...</h4>}
      next={() => {
        if (pageInfo?.hasNextPage) {
          fetchMore({ variables: { cursor: pageInfo.endCursor } });
        }
      }}
    >
      <Bookmarks nodes={nodes} />
    </InfiniteScroll>
  );
};

export default BookmarksWithData;
