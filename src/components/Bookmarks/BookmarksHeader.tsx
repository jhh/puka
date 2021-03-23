import { PlusOutlined, TagsOutlined } from "@ant-design/icons";
import { Button, Input } from "antd";
import { useNavigate } from "react-router-dom";
import AccountMenu from "../Shared/AccountMenu";
import styles from "./bookmarks.less";

type LogoProps = {
  onClick: () => void;
};

const Logo = (props: LogoProps) => {
  const navigate = useNavigate();
  return (
    <Button
      type="text"
      icon={<TagsOutlined className={styles.icon} />}
      className={styles.item}
      onClick={() => {
        props.onClick();
        navigate("");
      }}
    />
  );
};

function parseSearch(search: string): string {
  if (search.length === 0 || /^\s*$/.test(search)) return "";

  let queryTerms: string[] = [];
  let fullText: string = "";

  const words = search.split(" ");
  for (const word of words) {
    if (word.charAt(0) === "#") {
      queryTerms.push(`t=${word.slice(1)}`);
      continue;
    }
    if (fullText.length === 0) {
      fullText = `q=${word}`;
      continue;
    }
    fullText += "%20" + word;
  }
  if (fullText.length !== 0) queryTerms.push(fullText);

  return `?${queryTerms.join("&")}`;
}

type Props = {
  onCreateClick: () => void;
};

const { Search } = Input;

const Header = ({ onCreateClick }: Props) => {
  const navigate = useNavigate();

  return (
    <div className={styles.header}>
      <Logo onClick={() => {}} />
      <h2 className={`${styles.title} ${styles.item}`}>Bookmarks</h2>
      <Search
        placeholder="input search text"
        onSearch={(search) => {
          const query = parseSearch(search);
          navigate(query);
        }}
        className={`${styles.search} ${styles.item}`}
      />
      <div className={`${styles.spacer} ${styles.item}`} />
      <Button
        className={styles.item}
        type="text"
        icon={<PlusOutlined className={styles.icon} />}
        onClick={onCreateClick}
      />

      <AccountMenu />
    </div>
  );
};

export default Header;
