import { Typography } from "@material-ui/core";
import Link from "@material-ui/core/Link";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { AllBookmarks_allBookmarks_edges_node } from "../../generated/AllBookmarks";
import TagList from "../Tag/TagList";
import EditBookmark from "./EditBookmark";

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
      <Typography variant="caption" color="textSecondary">
        {date
          .toLocaleDateString("en-us", { year: "numeric", month: "long" })
          .toLowerCase()}
        <EditBookmark bookmark={bookmark} />
      </Typography>
    </div>
  );
};

const Bookmark = ({ bookmark }: BookmarkProps) => {
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
            <EditLine bookmark={bookmark} />
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
    edit: {
      paddingLeft: theme.spacing(1),
    },
  })
);

export default Bookmarks;
