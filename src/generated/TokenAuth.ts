/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL mutation operation: TokenAuth
// ====================================================

export interface TokenAuth_tokenAuth {
  __typename: "ObtainJSONWebToken";
  token: string;
}

export interface TokenAuth {
  /**
   * Obtain JSON Web Token mutation
   */
  tokenAuth: TokenAuth_tokenAuth | null;
}

export interface TokenAuthVariables {
  username: string;
  password: string;
}
