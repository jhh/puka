import AppBar from "@material-ui/core/AppBar";
import IconButton from "@material-ui/core/IconButton";
import InputBase from "@material-ui/core/InputBase";
import {
  createStyles,
  fade,
  makeStyles,
  Theme,
} from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import AddIcon from "@material-ui/icons/Add";
import SearchIcon from "@material-ui/icons/Search";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AccountMenu from "../Shared/AccountMenu";
import Logo from "../Shared/Logo";

type Props = {
  onCreateClick: () => void;
};

const Header = ({ onCreateClick }: Props) => {
  const classes = useStyles();
  const navigate = useNavigate();
  const [search, setSearch] = useState<string>("");

  return (
    <AppBar position="sticky" className={classes.root}>
      <Toolbar className={classes.toolbar}>
        <Logo onClick={() => setSearch("")} />
        <Typography variant="h6" className={classes.title}>
          Bookmarks
        </Typography>
        <div className={classes.search}>
          <div className={classes.searchIcon}>
            <SearchIcon />
          </div>
          <InputBase
            placeholder="Search…"
            value={search}
            classes={{
              root: classes.inputRoot,
              input: classes.inputInput,
            }}
            onChange={(ev) => setSearch(ev.target.value)}
            onKeyPress={(ev: any) => {
              if (ev.key === "Enter") {
                navigate(`?q=${search}`);
                ev.preventDefault();
              }
            }}
          />
        </div>
        <div className={classes.grow} />
        <IconButton>
          <AddIcon
            fontSize="large"
            className={classes.icon}
            onClick={onCreateClick}
          />
        </IconButton>
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
      padding: theme.spacing(0, 4),
    },
    icon: {
      color: theme.palette.common.white,
    },
    title: {
      display: "none",
      [theme.breakpoints.up("sm")]: {
        display: "block",
      },
    },
    grow: {
      flexGrow: 1,
    },
    search: {
      position: "relative",
      borderRadius: theme.shape.borderRadius,
      backgroundColor: fade(theme.palette.common.white, 0.15),
      "&:hover": {
        backgroundColor: fade(theme.palette.common.white, 0.25),
      },
      marginRight: theme.spacing(2),
      marginLeft: 0,
      width: "100%",
      [theme.breakpoints.up("sm")]: {
        marginLeft: theme.spacing(3),
        width: "auto",
      },
    },
    searchIcon: {
      padding: theme.spacing(0, 2),
      height: "100%",
      position: "absolute",
      pointerEvents: "none",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    inputRoot: {
      color: "inherit",
    },
    inputInput: {
      padding: theme.spacing(1, 1, 1, 0),
      // vertical padding + font size from searchIcon
      paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
      transition: theme.transitions.create("width"),
      width: "100%",
      [theme.breakpoints.up("md")]: {
        width: "20ch",
      },
    },
  })
);

export default Header;
