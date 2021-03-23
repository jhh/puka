import { UserOutlined } from "@ant-design/icons";
import { Button, Popover } from "antd";
import { useState } from "react";
import { isLoggedInVar } from "../../cache";
import styles from "./shared.less";

function handleSignout() {
  localStorage.removeItem("token");
  isLoggedInVar(false);
  window.location.reload();
}

const AccountMenu = () => {
  const [visible, setVisible] = useState(false);

  return (
    <Popover
      overlayClassName="accountMenu"
      content={
        <ul className={styles.menu}>
          <li>
            <Button
              type="text"
              className={styles.button}
              onClick={() => setVisible(false)}
            >
              Profile
            </Button>
          </li>
          <li>
            <Button
              type="text"
              className={styles.button}
              onClick={() => handleSignout()}
            >
              Sign Out
            </Button>
          </li>
        </ul>
      }
      trigger="click"
      visible={visible}
      onVisibleChange={(v) => setVisible(v)}
    >
      <Button
        type="text"
        icon={<UserOutlined className={styles.accountIcon} />}
      />
    </Popover>
  );
};

/*
const AccountMenu = () => {
  return (
    <Menu mode="horizontal" triggerSubMenuAction="click">
      <SubMenu icon={<UserOutlined id="accountIcon" />}>
        <Menu.Item key="1">Profile</Menu.Item>
        <Menu.Item key="2" onClick={() => handleSignout()}>
          Sign Out
        </Menu.Item>
      </SubMenu>
    </Menu>
  );
};
*/
export default AccountMenu;
