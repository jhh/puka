import Link from "@material-ui/core/Link";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import InfiniteScroll from "react-infinite-scroll-component";
import { Bookmarks } from "../../generated/Bookmarks";
import TagList from "../Tag/TagList";

type Props = Bookmarks & { fetchMore: any };

const BookmarkList = ({ bookmarks, fetchMore }: Props) => {
  const classes = useStyles();

  if (bookmarks === null) return null;

  return (
    <List dense>
      <InfiniteScroll
        dataLength={bookmarks.length}
        next={() =>
          fetchMore({
            variables: {
              offset: bookmarks.length,
            },
          })
        }
        hasMore={true}
        loader={<h4>Loading...</h4>}
      >
        {bookmarks.map((bm) => (
          <ListItem key={bm.id}>
            <ListItemText
              primary={
                <Link href={bm?.url} target="_blank" rel="noreferrer">
                  {bm.title}
                </Link>
              }
              primaryTypographyProps={{
                variant: "subtitle1",
                color: "primary",
              }}
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
      </InfiniteScroll>
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
