import Container from "@material-ui/core/Container";
import { useState } from "react";
import BookmarksHeader from "../components/Bookmarks/BookmarksHeader";
import BookmarksWithData from "../components/Bookmarks/BookmarkWithData";
import CreateBookmark from "../components/Bookmarks/CreateBookmark";

const Bookmarks = () => {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <>
      <BookmarksHeader onCreateClick={() => setOpen(true)} />
      <Container maxWidth="md">
        <BookmarksWithData />
        <CreateBookmark open={open} setOpen={setOpen} />
      </Container>
    </>
  );
};

export default Bookmarks;
