import AppBar from "@material-ui/core/AppBar";
import IconButton from "@material-ui/core/IconButton";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import BookmarksIcon from "@material-ui/icons/Bookmarks";
// import { Link } from "react-router-dom";
import AccountCircle from "@material-ui/icons/AccountCircle";
import MenuItem from "@material-ui/core/MenuItem";
import Menu from "@material-ui/core/Menu";
import { useState } from "react";
import Signout from "../Auth/Signout";

const Header = () => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState<Element | null>(null);

  const handleClose: React.MouseEventHandler<HTMLLIElement> = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar position="sticky" className={classes.root}>
      <Toolbar className={classes.toolbar}>
        <IconButton edge="start" className={classes.logoButton}>
          <BookmarksIcon fontSize="large" className={classes.icon} />
        </IconButton>
        <Typography variant="h6" className={classes.title}>
          Puka
        </Typography>
        <div>
          <IconButton
            edge="end"
            onClick={(event) => setAnchorEl(event.currentTarget)}
          >
            <AccountCircle fontSize="large" className={classes.icon} />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleClose}>Profile</MenuItem>
            <Signout />
          </Menu>
        </div>
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
    menuIcon: {
      //
    },
    title: {
      flexGrow: 1,
    },
  })
);

export default Header;
