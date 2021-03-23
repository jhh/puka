import { Link } from "react-router-dom";
import styles from "./tag.less";

type Props = {
  tags: string[];
};

const TagList = ({ tags }: Props) => {
  return (
    <span className={styles.tags}>
      {tags.map((tag) => (
        <Link to={`?t=${tag}`} key={tag}>
          {tag}
        </Link>
      ))}
    </span>
  );
};

export default TagList;
