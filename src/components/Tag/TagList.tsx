import { Typography } from "@material-ui/core";
import { Link } from "react-router-dom";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";

type Props = {
  tags: string[];
};

const TagList = ({ tags }: Props) => {
  const classes = useStyles();

  return (
    <Typography variant="body2" color="textPrimary" component="div">
      {tags.map((tag) => (
        <Link to={`?t=${tag}`} key={tag} className={classes.link}>
          {tag}
        </Link>
      ))}
    </Typography>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    link: {
      paddingRight: theme.spacing(1),
      color: theme.palette.primary.light,
      textDecoration: "none",
      "&:hover": {
        textDecoration: "underline",
      },
    },
  })
);

export default TagList;
