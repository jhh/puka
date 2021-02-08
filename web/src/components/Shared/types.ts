export interface Bookmark {
    id: number;
    title: string;
    description: string;
    url: string;
    tags: string[];
    createdAt: Date;
  }
  
  export interface BookmarkData {
    bookmarks: Bookmark[];
  }