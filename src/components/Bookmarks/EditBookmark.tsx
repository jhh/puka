import { gql, useMutation } from "@apollo/client";
import { Form, Modal } from "antd";
import { useState } from "react";
import {
  UpdateBookmark,
  UpdateBookmarkVariables,
  UpdateBookmark_updateBookmark_bookmark,
} from "../../generated/UpdateBookmark";
import BookmarkForm from "./BookmarkForm";
import styles from "./bookmarks.less";

const UPDATE_BOOKMARK_MUTATION = gql`
  mutation UpdateBookmark(
    $id: ID!
    $title: String!
    $description: String
    $url: String!
    $tags: [String]
  ) {
    updateBookmark(
      input: {
        id: $id
        title: $title
        description: $description
        url: $url
        tags: $tags
      }
    ) {
      bookmark {
        id
        title
        description
        url
        tags
        createdAt
      }
    }
  }
`;

type Props = {
  bookmark: UpdateBookmark_updateBookmark_bookmark;
};

const EditBookmark = ({ bookmark }: Props) => {
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const [updateBookmark] = useMutation<UpdateBookmark, UpdateBookmarkVariables>(
    UPDATE_BOOKMARK_MUTATION
  );

  const onUpdate = async (values: any) => {
    const tagsArray = values.tags
      .split(",")
      .map((t: string) => t.trim())
      .filter((t: string) => t.length > 0);

    const variables: UpdateBookmarkVariables = {
      ...values,
      id: bookmark.id,
      tags: tagsArray,
    };

    await updateBookmark({ variables });
    setOpen(false);
  };

  return (
    <>
      <span className={styles.edit} onClick={() => setOpen(true)}>
        edit
      </span>
      <Modal
        visible={open}
        title="Update bookmark"
        okText="Update"
        cancelText="Cancel"
        onCancel={() => {
          form.resetFields();
          setOpen(false);
        }}
        onOk={() => {
          form
            .validateFields()
            .then((values) => {
              form.resetFields();
              onUpdate(values);
            })
            .catch((info) => {
              console.log("Validate Failed:", info);
            });
        }}
      >
        <BookmarkForm bookmark={bookmark} form={form} />
      </Modal>
    </>
  );
};

export default EditBookmark;
