import { useState } from "react";
import AddBookmark from "../components/Bookmarks/AddBookmark";
import BookmarksHeader from "../components/Bookmarks/BookmarksHeader";
import BookmarksWithData from "../components/Bookmarks/BookmarkWithData";
import { Layout } from "antd";
import styles from "./pages.less";

const { Content, Header, Footer } = Layout;

const Bookmarks = () => {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <Layout className={styles.layout}>
      <Header className={styles.header}>
        <BookmarksHeader onCreateClick={() => setOpen(true)} />
      </Header>
      <Content className={styles.layoutContent}>
        <div className={styles.bookmarksContent}>
          <BookmarksWithData />
        </div>
        <AddBookmark open={open} setOpen={setOpen} />
      </Content>
      <Footer className={styles.footer}>Footer</Footer>
    </Layout>
  );
};

export default Bookmarks;
