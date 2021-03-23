import { gql, useMutation } from "@apollo/client";
import { Dispatch, SetStateAction } from "react";
import { Form, Modal } from "antd";
import BookmarkForm from "./BookmarkForm";
import {
  CreateBookmark,
  CreateBookmarkVariables,
} from "../../generated/CreateBookmark";

const CREATE_BOOKMARK_MUTATION = gql`
  mutation CreateBookmark(
    $title: String!
    $description: String
    $url: String!
    $tags: [String]
  ) {
    createBookmark(
      input: {
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
  open: boolean;
  setOpen: Dispatch<SetStateAction<boolean>>;
};

const AddBookmark = ({ open, setOpen }: Props) => {
  const [createBookmark] = useMutation<CreateBookmark, CreateBookmarkVariables>(
    CREATE_BOOKMARK_MUTATION,
    {
      update(cache, { data }) {
        if (!data?.createBookmark) return;

        cache.modify({
          fields: {
            allBookmarks(existingBookmarks = {}) {
              const newBookmarkRef = cache.writeFragment({
                data: data.createBookmark?.bookmark,
                fragment: gql`
                  fragment NewBookmarkNode on BookmarkNode {
                    id
                    title
                    description
                    url
                    tags
                    createdAt
                  }
                `,
              });
              // graphene-relay pagination cursor is base64-encoded offset
              // into the query results. Since we insert our new element
              // at the head of the cached results but don't update the offset,
              // we end up with a duplicate in the cache when refetch occurs.
              // (last element of previous page is also first element of next page)
              //
              // We prevent this by removing the last cached element and
              // moving the cursor info to the new last element. On refetch
              // the removed element will be the element at cursor offset.
              const edgeCount = existingBookmarks.edges.length;
              return {
                edges: [
                  { __typename: "BookmarkNodeEdge", node: newBookmarkRef },

                  ...existingBookmarks.edges.slice(0, -2),

                  {
                    ...existingBookmarks.edges[edgeCount - 2],
                    cursor: existingBookmarks.pageInfo.endCursor,
                  },
                ],
                pageInfo: existingBookmarks.pageInfo,
                __typename: "BookmarkNodeConnection",
              };
            },
          },
        });
      },
    }
  );

  const onCreate = async (values: any) => {
    const tagsArray = values.tags
      .split(",")
      .map((t: string) => t.trim())
      .filter((t: string) => t.length > 0);

    const variables: CreateBookmarkVariables = {
      ...values,
      tags: tagsArray,
    };

    await createBookmark({ variables });
    setOpen(false);
  };

  const [form] = Form.useForm();
  return (
    <Modal
      visible={open}
      title="Create bookmark"
      okText="Create"
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
            onCreate(values);
          })
          .catch((info) => {
            console.log("Validate Failed:", info);
          });
      }}
    >
      <BookmarkForm form={form} />
    </Modal>
  );
};

export default AddBookmark;
