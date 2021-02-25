/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL query operation: Bookmarks
// ====================================================

export interface Bookmarks_bookmarks {
  __typename: "BookmarkType";
  id: string;
  title: string;
  description: string;
  url: string;
  tags: string[];
  createdAt: any;
}

export interface Bookmarks {
  bookmarks: Bookmarks_bookmarks[] | null;
}

export interface BookmarksVariables {
  search?: string | null;
  tags?: (string | null)[] | null;
  offset?: number | null;
  limit?: number | null;
}
