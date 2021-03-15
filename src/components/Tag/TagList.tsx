import { Typography } from "@material-ui/core";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { Link } from "react-router-dom";

type Props = {
  tags: string[];
};

const TagList = ({ tags }: Props) => {
  const classes = useStyles();

  return (
    <Typography variant="subtitle2" color="textPrimary" component="div">
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
      color: theme.palette.secondary.light,
      textDecoration: "none",
      "&:hover": {
        textDecoration: "underline",
      },
    },
  })
);

export default TagList;
