import IconButton from "@material-ui/core/IconButton";
import BookmarksIcon from "@material-ui/icons/Bookmarks";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { useNavigate } from "react-router-dom";

type Props = {
  onClick: () => void;
};

const Logo = (props: Props) => {
  const classes = useStyles();
  const navigate = useNavigate();

  return (
    <IconButton
      edge="start"
      className={classes.logoButton}
      onClick={() => {
        props.onClick();
        navigate("");
      }}
    >
      <BookmarksIcon fontSize="large" className={classes.icon} />
    </IconButton>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    icon: {
      color: theme.palette.common.white,
    },
    logoButton: {
      marginRight: theme.spacing(1),
    },
  })
);

export default Logo;
