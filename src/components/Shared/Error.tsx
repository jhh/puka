import { ApolloError } from "@apollo/client";
import Button from "@material-ui/core/Button";
import Snackbar from "@material-ui/core/Snackbar";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { useState } from "react";

type Props = {
  error: ApolloError;
};

const Error = ({ error }: Props) => {
  const [open, setOpen] = useState(true);
  const classes = useStyles();

  return (
    <Snackbar
      className={classes.snackbar}
      open={open}
      message={error.message}
      action={
        <Button onClick={() => setOpen(false)} color="secondary" size="small">
          Close
        </Button>
      }
    />
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    snackbar: {
      margin: theme.spacing(1),
    },
  })
);

export default Error;
