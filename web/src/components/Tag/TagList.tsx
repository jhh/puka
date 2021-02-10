import { Typography } from "@material-ui/core";
import Link from "@material-ui/core/Link";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";

type Props = {
  tags: string[];
};

const TagList = ({ tags }: Props) => {
  const classes = useStyles();

  function handleClick(event: React.MouseEvent) {
    event.preventDefault();
  }

  return (
    <Typography variant="body2" color="textPrimary" component="div">
      {tags.map((tag) => (
        <Link
          href="http://example.com"
          onClick={handleClick}
          key={tag}
          className={classes.link}
        >
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
    },
  })
);

export default TagList;
