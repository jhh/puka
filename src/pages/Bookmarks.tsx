import Container from "@material-ui/core/Container";
import { useState } from "react";
import BookmarksHeader from "../components/Bookmarks/BookmarksHeader";
import BookmarksWithData from "../components/Bookmarks/BookmarkWithData";
import AddBookmark from "../components/Bookmarks/AddBookmark";

const Bookmarks = () => {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <>
      <BookmarksHeader onCreateClick={() => setOpen(true)} />
      <Container maxWidth="md">
        <BookmarksWithData />
        <AddBookmark open={open} setOpen={setOpen} />
      </Container>
    </>
  );
};

export default Bookmarks;
