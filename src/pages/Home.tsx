import Container from "@material-ui/core/Container";
// import { useEffect } from "react";
// import { useSearchParams } from "react-router-dom";
import BookmarksWithData from "../components/Bookmark/BookmarkWithData";
import CreateBookmark from "../components/Bookmark/CreateBookmark";

const Home = () => {
  // const [searchParams] = useSearchParams({});
  // const query = searchParams.get("q");
  // const tags = searchParams.getAll("t");

  // useEffect(() => {
  //   console.debug({ query, tags });
  // }, [query, JSON.stringify(tags)]);

  // if (query) variables.search = query;
  // if (tags.length > 0) variables.tags = tags.join(",");

  return (
    <Container>
      <BookmarksWithData />
      <CreateBookmark />
    </Container>
  );
};

export default Home;
