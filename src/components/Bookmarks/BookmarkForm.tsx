import { Form, FormInstance, Input } from "antd";
import { UpdateBookmark_updateBookmark_bookmark } from "../../generated/UpdateBookmark";

type BookmarkFormProps = {
  bookmark?: UpdateBookmark_updateBookmark_bookmark;
  form: FormInstance<any>;
};

const EMPTY_BOOKMARK: UpdateBookmark_updateBookmark_bookmark = {
  __typename: "BookmarkNode",
  id: "",
  title: "",
  description: "",
  url: "",
  tags: [],
  createdAt: null,
};

const BookmarkForm = ({ bookmark, form }: BookmarkFormProps) => {
  const init = bookmark ? bookmark : EMPTY_BOOKMARK;

  return (
    <Form
      form={form}
      layout="vertical"
      name="form_in_modal"
      initialValues={{
        title: init.title,
        description: init.description,
        url: init.url,
        tags: init.tags.join(", "),
      }}
    >
      <Form.Item
        name="title"
        label="Title"
        rules={[
          {
            required: true,
            message: "Please input the title of bookmark!",
          },
        ]}
      >
        <Input />
      </Form.Item>
      <Form.Item name="description" label="Description">
        <Input.TextArea autoSize />
      </Form.Item>
      <Form.Item
        name="url"
        label="URL"
        rules={[
          {
            required: true,
            message: "Please input the URL of bookmark!",
          },
        ]}
      >
        <Input type="url" />
      </Form.Item>
      <Form.Item name="tags" label="Tags">
        <Input />
      </Form.Item>
    </Form>
  );
};

export default BookmarkForm;
