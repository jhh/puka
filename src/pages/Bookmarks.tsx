import Container from "@material-ui/core/Container";
import BookmarksWithData from "../components/Bookmark/BookmarkWithData";
import CreateBookmark from "../components/Bookmark/CreateBookmark";
import Header from "../components/Shared/Header";

const Bookmarks = () => {
  return (
    <>
      <Header />
      <Container>
        <BookmarksWithData />
        <CreateBookmark />
      </Container>
    </>
  );
};

export default Bookmarks;
