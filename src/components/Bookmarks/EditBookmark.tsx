import { gql, useMutation } from "@apollo/client";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import { useState } from "react";
import {
  UpdateBookmark,
  UpdateBookmarkVariables,
  UpdateBookmark_updateBookmark_bookmark,
} from "../../generated/UpdateBookmark";

const UPDATE_BOOKMARK_MUTATION = gql`
  mutation UpdateBookmark(
    $id: ID!
    $title: String!
    $description: String
    $url: String!
    $tags: [String]
  ) {
    updateBookmark(
      input: {
        id: $id
        title: $title
        description: $description
        url: $url
        tags: $tags
      }
    ) {
      bookmark {
        id
        title
        description
        url
        tags
        createdAt
      }
    }
  }
`;

type Props = {
  bookmark: UpdateBookmark_updateBookmark_bookmark;
};

const EditBookmark = ({ bookmark }: Props) => {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState<string>(bookmark.title);
  const [description, setDescription] = useState<string>(bookmark.description);
  const [url, setUrl] = useState<string>(bookmark.url);
  const [tags, setTags] = useState<string>(bookmark.tags.join(","));
  const [updateBookmark] = useMutation<UpdateBookmark, UpdateBookmarkVariables>(
    UPDATE_BOOKMARK_MUTATION
  );

  const handleSubmit = async () => {
    const tagsArray = tags
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    await updateBookmark({
      variables: { id: bookmark.id, title, description, url, tags: tagsArray },
    });

    setOpen(false);
  };

  return (
    <>
      <span className={classes.root} onClick={() => setOpen(true)}>
        edit
      </span>
      <Dialog open={open}>
        <DialogTitle>Edit Bookmark</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="title"
            label="Title"
            fullWidth
            value={title}
            onChange={(event: any) => setTitle(event.target.value)}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description"
            fullWidth
            multiline
            value={description}
            onChange={(event: any) => setDescription(event.target.value)}
          />
          <TextField
            margin="dense"
            id="url"
            label="URL"
            fullWidth
            value={url}
            onChange={(event: any) => setUrl(event.target.value)}
          />
          <TextField
            margin="dense"
            id="tags"
            label="Tags"
            fullWidth
            value={tags}
            onChange={(event: any) => setTags(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color="primary">
            Cancel
          </Button>
          <Button color="primary" onClick={() => handleSubmit()}>
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      paddingLeft: theme.spacing(1),
      "&:hover": {
        cursor: "pointer",
      },
    },
  })
);

export default EditBookmark;
