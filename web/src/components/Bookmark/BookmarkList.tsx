import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
// import { FixedSizeList, ListChildComponentProps } from "react-window";
import { BookmarkData } from "../Shared/types";
import UpdateBookmark from "./UpdateBookmark";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { Typography } from "@material-ui/core";

type Props = BookmarkData;

function openInNewTab(url: string) {
  const newWindow = window.open(url, "_blank", "noopener,noreferrer");
  if (newWindow) newWindow.opener = null;
}

const BookmarkList = ({ bookmarks }: Props) => {
  const classes = useStyles();
  return (
    <List dense>
      {bookmarks.map((bm) => (
        <ListItem button key={bm.id} onClick={() => openInNewTab(bm.url)}>
          <ListItemText
            primary={bm.title}
            primaryTypographyProps={{ variant: "subtitle1", color: "primary" }}
            secondary={
              <>
                {bm.description}
                <Typography variant="body2" color="textPrimary">
                  {bm.tags.join(", ")}
                </Typography>
              </>
            }
            className={classes.listText}
          />
          <ListItemSecondaryAction>
            <UpdateBookmark />
          </ListItemSecondaryAction>
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
