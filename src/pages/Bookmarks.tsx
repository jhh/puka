import Container from "@material-ui/core/Container";
import BookmarksWithData from "../components/Bookmarks/BookmarkWithData";
import CreateBookmark from "../components/Bookmarks/CreateBookmark";
import Header from "../components/Bookmarks/BookmarksHeader";

const Bookmarks = () => {
  return (
    <>
      <Header />
      <Container maxWidth="md">
        <BookmarksWithData />
        <CreateBookmark />
      </Container>
    </>
  );
};

export default Bookmarks;
