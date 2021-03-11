/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL query operation: AllBookmarks
// ====================================================

export interface AllBookmarks_allBookmarks_pageInfo {
  __typename: "PageInfo";
  /**
   * When paginating forwards, the cursor to continue.
   */
  endCursor: string | null;
  /**
   * When paginating forwards, are there more items?
   */
  hasNextPage: boolean;
}

export interface AllBookmarks_allBookmarks_edges_node {
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

export interface AllBookmarks_allBookmarks_edges {
  __typename: "BookmarkNodeEdge";
  /**
   * The item at the end of the edge
   */
  node: AllBookmarks_allBookmarks_edges_node | null;
}

export interface AllBookmarks_allBookmarks {
  __typename: "BookmarkNodeConnection";
  /**
   * Pagination data for this connection.
   */
  pageInfo: AllBookmarks_allBookmarks_pageInfo;
  /**
   * Contains the nodes in this connection.
   */
  edges: (AllBookmarks_allBookmarks_edges | null)[];
}

export interface AllBookmarks {
  allBookmarks: AllBookmarks_allBookmarks | null;
}

export interface AllBookmarksVariables {
  search?: string | null;
  tags?: string | null;
  cursor?: string | null;
}
