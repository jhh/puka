import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { BookmarkData } from "../Shared/types";
import Link from "@material-ui/core/Link";
// import UpdateBookmark from "./UpdateBookmark";
import TagList from "../Tag/TagList";

type Props = BookmarkData;

const BookmarkList = ({ bookmarks }: Props) => {
  const classes = useStyles();
  return (
    <List dense>
      {bookmarks.map((bm) => (
        <ListItem key={bm.id}>
          <ListItemText
            primary={
              <Link href={bm.url} target="_blank" rel="noreferrer">
                {bm.title}
              </Link>
            }
            primaryTypographyProps={{ variant: "subtitle1", color: "primary" }}
            secondary={
              <>
                {bm.description}
                <TagList tags={bm.tags} />
              </>
            }
            secondaryTypographyProps={{ component: "div" }}
            className={classes.listText}
          />
        </ListItem>
      ))}
    </List>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    listText: {
      paddingRight: theme.spacing(4),
    },
  })
);

export default BookmarkList;
