import { ApolloError } from "@apollo/client";
import { message } from "antd";

type Props = {
  error: ApolloError;
};

const Error = ({ error }: Props) => {
  message.error(error.message);
  return <></>;
};

export default Error;
