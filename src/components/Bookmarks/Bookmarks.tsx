import Link from "@material-ui/core/Link";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { AllBookmarks_allBookmarks_edges_node } from "../../generated/AllBookmarks";
import TagList from "../Tag/TagList";

type BookmarksProps = {
  nodes: (AllBookmarks_allBookmarks_edges_node | null)[];
};

type BookmarkProp = {
  bookmark: AllBookmarks_allBookmarks_edges_node;
};

const Bookmark = ({ bookmark }: BookmarkProp) => {
  const classes = useStyles();

  return (
    <ListItem>
      <ListItemText
        primary={
          <Link
            href={bookmark.url}
            className={classes.title}
            target="_blank"
            rel="noreferrer"
          >
            {bookmark.title}
          </Link>
        }
        primaryTypographyProps={{
          variant: "subtitle1",
          color: "textPrimary",
        }}
        secondary={
          <>
            {bookmark.description}
            <TagList tags={bookmark.tags} />
          </>
        }
        secondaryTypographyProps={{ component: "div" }}
        className={classes.listText}
      />
    </ListItem>
  );
};

const Bookmarks = ({ nodes }: BookmarksProps) => (
  <List dense>
    {nodes.map((bookmark) => {
      if (bookmark === null) {
        throw new Error("Bookmark bookmark property was null");
      }
      return <Bookmark key={bookmark.id} bookmark={bookmark} />;
    })}
  </List>
);

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    listText: {
      paddingRight: theme.spacing(4),
    },
    title: {
      "&:hover": {
        textDecoration: "none",
      },
    },
  })
);

export default Bookmarks;
