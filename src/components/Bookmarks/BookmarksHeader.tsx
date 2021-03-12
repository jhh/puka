import AppBar from "@material-ui/core/AppBar";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import AccountMenu from "../Shared/AccountMenu";
import Logo from "../Shared/Logo";

const Header = () => {
  const classes = useStyles();

  return (
    <AppBar position="sticky" className={classes.root}>
      <Toolbar className={classes.toolbar}>
        <Logo />
        <Typography variant="h6" className={classes.title}>
          Puka Bookmarks
        </Typography>
        <AccountMenu />
      </Toolbar>
    </AppBar>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      alignItems: "center",
    },
    toolbar: {
      maxWidth: theme.breakpoints.values.md,
      width: "100%",
      padding: `0 ${theme.spacing(4)}px`,
    },
    icon: {
      color: theme.palette.common.white,
    },
    logoButton: {
      marginRight: theme.spacing(1),
    },
    title: {
      flexGrow: 1,
    },
  })
);

export default Header;
