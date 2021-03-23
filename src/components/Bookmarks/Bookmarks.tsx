import { List } from "antd";
import { AllBookmarks_allBookmarks_edges_node } from "../../generated/AllBookmarks";
import TagList from "../Tag/TagList";
import EditBookmark from "./EditBookmark";
import styles from "./bookmarks.less";

type BookmarksProps = {
  nodes: (AllBookmarks_allBookmarks_edges_node | null)[];
};

type BookmarkProps = {
  bookmark: AllBookmarks_allBookmarks_edges_node;
};

const EditLine = ({ bookmark }: BookmarkProps) => {
  const date = new Date(bookmark.createdAt);
  return (
    <div>
      <span className={styles.editLine}>
        {date
          .toLocaleDateString("en-us", { year: "numeric", month: "long" })
          .toLowerCase()}
        <EditBookmark bookmark={bookmark} />
      </span>
    </div>
  );
};

const Bookmark = ({ bookmark }: BookmarkProps) => {
  return (
    <List.Item>
      <List.Item.Meta
        title={
          <a href={bookmark.url} target="_blank" rel="noreferrer">
            {bookmark.title}
          </a>
        }
        description={bookmark.description}
      />
      <TagList tags={bookmark.tags} />
      <EditLine bookmark={bookmark} />
    </List.Item>
  );
};

const Bookmarks = ({ nodes }: BookmarksProps) => (
  <List
    itemLayout="vertical"
    dataSource={nodes}
    renderItem={(bookmark) => {
      if (bookmark === null) throw new Error("Bookmark was null");
      return <Bookmark key={bookmark.id} bookmark={bookmark} />;
    }}
  />
);

export default Bookmarks;
