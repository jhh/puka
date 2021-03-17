import { gql, useMutation } from "@apollo/client";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import TextField from "@material-ui/core/TextField";
import { Dispatch, SetStateAction, useState } from "react";
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
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [url, setUrl] = useState<string>("");
  const [tags, setTags] = useState<string>("");
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

  const handleSubmit = async () => {
    const tagsArray = tags
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    await createBookmark({
      variables: { title, description, url, tags: tagsArray },
    });

    setTitle("");
    setDescription("");
    setUrl("");
    setTags("");
    setOpen(false);
  };

  return (
    <>
      <Dialog open={open}>
        <DialogTitle>Add Bookmark</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="title"
            label="Title"
            fullWidth
            value={title}
            onChange={(event: any) => setTitle(event.target.value)}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description"
            fullWidth
            multiline
            value={description}
            onChange={(event: any) => setDescription(event.target.value)}
          />
          <TextField
            margin="dense"
            id="url"
            label="URL"
            fullWidth
            value={url}
            onChange={(event: any) => setUrl(event.target.value)}
          />
          <TextField
            margin="dense"
            id="tags"
            label="Tags"
            fullWidth
            value={tags}
            onChange={(event: any) => setTags(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color="primary">
            Cancel
          </Button>
          <Button color="primary" onClick={() => handleSubmit()}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AddBookmark;
