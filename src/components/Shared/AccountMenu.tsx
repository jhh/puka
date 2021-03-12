import AccountCircle from "@material-ui/icons/AccountCircle";
import MenuItem from "@material-ui/core/MenuItem";
import Menu from "@material-ui/core/Menu";
import Signout from "../Auth/Signout";
import IconButton from "@material-ui/core/IconButton";
import { useState } from "react";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";

const AccountMenu = () => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState<Element | null>(null);

  const handleClose: React.MouseEventHandler<HTMLLIElement> = () => {
    setAnchorEl(null);
  };
  return (
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
        <MenuItem
          onClick={() => {
            window.location.assign("/admin/");
          }}
        >
          Admin
        </MenuItem>
        <Signout />
      </Menu>
    </div>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    icon: {
      color: theme.palette.common.white,
    },
  })
);

export default AccountMenu;
