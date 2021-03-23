// import { useNavigate } from "react-router-dom";

type Props = {
  onClick: () => void;
};

const Logo = (props: Props) => {
  console.log(props);
  // const navigate = useNavigate();

  return (
    <div>Logo</div>
    /*
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
    */
  );
};

// const useStyles = makeStyles((theme: Theme) =>
//   createStyles({
//     icon: {
//       color: theme.palette.common.white,
//     },
//     logoButton: {
//       marginRight: theme.spacing(1),
//     },
//   })
// );

export default Logo;
