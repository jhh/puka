import json
from graphene_django.utils.testing import GraphQLTestCase


class BookmarkTestCase(GraphQLTestCase):
    def test_some_query(self):
        query = """
            {
                bookmarks {
                    id
                }
            }
            """
        response = self.query(query)
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content["data"]["bookmarks"]), 10)

    # def auth_header(self):
    #     response = self.query(
    #         """
    #         mutation {
    #             createUser(username:"test", email:"test@example.com", password:"test") {
    #                 user {
    #                     username
    #                 }
    #             }
    #         }
    #         """
    #     )
    #     content = json.loads(response.content)
    #     self.assertResponseNoErrors(response)
    #     self.assertEqual(content["data"]["createUser"]["user"]["username"], "test")

    #     response = self.query(
    #         """
    #         mutation {
    #             tokenAuth(username:"test", password:"test") {
    #                 token
    #             }
    #         }
    #         """
    #     )
    #     content = json.loads(response.content)
    #     self.assertResponseNoErrors(response)
    #     token = content["data"]["tokenAuth"]["token"]
    #     return {"Authorization": f"JWT {token}"}

    # def test_me_query(self):
    #     user = get_user_model().objects.create(username="test")
    #     client = Client()
    #     client.force_login(user)
    #     response = self.query(
    #         """
    #         {
    #             me {
    #                 email
    #             }
    #         }
    #         """,
    #         headers=self.auth_header()
    #     )
    #     content = json.loads(response.content)
    #     self.assertResponseNoErrors(response)
