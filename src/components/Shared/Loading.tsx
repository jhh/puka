import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";

const Loading = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <CircularProgress className={classes.progress} />
    </div>
  );
};

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100vw",
    textAlign: "center",
  },
  progress: {
    margin: theme.spacing(2),
    color: theme.palette.secondary.dark,
  },
}));

export default Loading;
