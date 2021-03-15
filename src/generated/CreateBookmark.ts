/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL mutation operation: CreateBookmark
// ====================================================

export interface CreateBookmark_createBookmark_bookmark {
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

export interface CreateBookmark_createBookmark {
  __typename: "CreateBookmarkPayload";
  bookmark: CreateBookmark_createBookmark_bookmark | null;
}

export interface CreateBookmark {
  createBookmark: CreateBookmark_createBookmark | null;
}

export interface CreateBookmarkVariables {
  title: string;
  description?: string | null;
  url: string;
  tags?: (string | null)[] | null;
}
