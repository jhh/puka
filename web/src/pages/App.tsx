import { gql, useQuery } from "@apollo/client";
import Container from "@material-ui/core/Container";
// import { createStyles, makeStyles } from "@material-ui/core/styles";
import Loading from "../components/Shared/Loading";
import Error from "../components/Shared/Error";
import { BookmarkData } from "../components/Shared/types";
import BookmarkList from "../components/Bookmark/BookmarkList";

const App = () => {
  // const classes = useStyles();
  const { loading, error, data } = useQuery<BookmarkData>(BOOKMARKS_QUERY);

  let content: JSX.Element;

  if (error) {
    content = <Error />;
  } else if (loading) {
    content = <Loading />;
  } else if (data) {
    content = <BookmarkList bookmarks={data.bookmarks} />;
  } else {
    content = <></>;
  }

  return <Container>{content}</Container>;
};

// const useStyles = makeStyles(() =>
//   createStyles({
//     root: {
//       margin: "0 auto",
//     },
//   })
// );

export default App;

const BOOKMARKS_QUERY = gql`
  {
    bookmarks(offset: 0, limit: 100) {
      id
      title
      description
      url
      tags
      createdAt
    }
  }
`;
