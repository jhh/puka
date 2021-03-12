import Fab from "@material-ui/core/Fab";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import AddIcon from "@material-ui/icons/Add";
import ClearIcon from "@material-ui/icons/Clear";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { useState } from "react";

const CreateBookmark = () => {
  const classes = useStyles();
  const [open, setOpen] = useState<boolean>(false);
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [url, setUrl] = useState<string>("");
  //   const [tags, setTags] = useState<string[]>([]);

  const handleSubmit = () => {
    console.log({ title, description, url });
  };

  return (
    <>
      <Fab
        onClick={() => setOpen(true)}
        color="secondary"
        className={classes.fab}
      >
        {open ? <ClearIcon /> : <AddIcon />}
      </Fab>
      <Dialog open={open}>
        <DialogTitle>Add Bookmark</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="title"
            label="Title"
            fullWidth
            onChange={(event) => setTitle(event.target.value)}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description"
            fullWidth
            onChange={(event) => setDescription(event.target.value)}
          />
          <TextField
            margin="dense"
            id="url"
            label="URL"
            fullWidth
            onChange={(event) => setUrl(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color="primary">
            Cancel
          </Button>
          <Button color="primary" onClick={() => handleSubmit()}>
            Subscribe
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    fab: {
      position: "fixed",
      bottom: theme.spacing(2),
      right: theme.spacing(2),
      zIndex: 200,
    },
  })
);

export default CreateBookmark;
