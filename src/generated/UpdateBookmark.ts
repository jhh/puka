/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL mutation operation: UpdateBookmark
// ====================================================

export interface UpdateBookmark_updateBookmark_bookmark {
  __typename: "BookmarkNode";
  /**
   * The ID of the object.
   */
  id: string;
  title: string;
  description: string;
  url: string;
  tags: string[];
  createdAt: any;
}

export interface UpdateBookmark_updateBookmark {
  __typename: "UpdateBookmarkPayload";
  bookmark: UpdateBookmark_updateBookmark_bookmark | null;
}

export interface UpdateBookmark {
  updateBookmark: UpdateBookmark_updateBookmark | null;
}

export interface UpdateBookmarkVariables {
  id: string;
  title: string;
  description?: string | null;
  url: string;
  tags?: (string | null)[] | null;
}
