import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Form, Input } from "antd";
import { TokenAuthVariables } from "../../generated/TokenAuth";
import styles from "./auth.less";

type LoginFormProps = {
  login: (a: { variables: TokenAuthVariables }) => void;
};

export default function SignIn(props: LoginFormProps) {
  const onFinish = (values: any) => {
    const variables: TokenAuthVariables = {
      username: values.username,
      password: values.password,
    };
    props.login({ variables });
  };

  return (
    <div>
      <Form
        name="normal_login"
        initialValues={{ remember: true }}
        className={styles.loginForm}
        onFinish={onFinish}
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: "Please input your Username!" }]}
        >
          <Input
            prefix={<UserOutlined className="site-form-item-icon" />}
            placeholder="Username"
            autoComplete="username"
          />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: "Please input your Password!" }]}
        >
          <Input
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            placeholder="Password"
            autoComplete="current-password"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit">
            Log in
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
