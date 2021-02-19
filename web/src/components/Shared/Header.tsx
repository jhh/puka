import AppBar from "@material-ui/core/AppBar";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import BookmarksIcon from "@material-ui/icons/Bookmarks";
import { Link } from "react-router-dom";

import Signout from "../Auth/Signout";

const Header = () => {
  const classes = useStyles();
  return (
    <AppBar position="sticky" className={classes.root}>
      <Toolbar>
        <Link to="/" className={classes.link}>
          <BookmarksIcon className={classes.icon} />
        </Link>
        <Typography variant="h6" className={classes.title}>
          Puka
        </Typography>
        <Signout />
      </Toolbar>
    </AppBar>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      flexGrow: 1,
    },
    icon: {
      marginRight: theme.spacing(2),
      fontSize: "2rem",
    },
    title: {
      flexGrow: 1,
    },
    link: {
      textDecoration: "none",
      color: theme.palette.common.white,
    },
  })
);

export default Header;
