from unittest import TestCase, main
from elasticsearch import Elasticsearch


class TestElasticsearch(TestCase):
    def setUp(self):
        self.client = Elasticsearch()

    def test_connect_to_server(self):
        """Non-java clients connect to Elasticsearch via the REST api,
        which runs on port 9200 by default."""

        Elasticsearch(
            host="localhost",
            port=9200
        )

    def test_index_document(self):
        """Elasticsearch can store arbitrary documents"""
        post = {
            "title": "My Document",
            "body": "Hello world."
        }

        # Documents in elasticsearch have an INDEX and a
        # TYPE. You can also specify an ID here if you
        # want to generate your own.
        self.client.index(
            index="blog",  # Think "database"
            doc_type="post",
            body=post
        )

    def test_search_all(self):
        """Elasticsearch can search for your documents in many ways.
        """
        post_1 = {
            "title": "Hello World",
            "body": "This is a post"
        }

        post_2 = {
            "title": "Camp Grenada",
            "body": "Hello mother, hello father."
        }

        self.client.delete_by_query(
            index="blog",
            body={'query': {"match_all": {}}}
        )

        for post in [post_1, post_2]:
            self.client.index(
                index="blog",
                doc_type="post",
                body=post)

        # If the index is not refreshed, we won't find our documents
        # right away.
        self.client.indices.refresh(index="blog")

        query = {
            'term': {            # Search for a given term
                '_all': 'hello'  # in any field (_all is a special wildcard)
            }
        }

        search_result = self.client.search(
            index="blog",
            doc_type="post",
            body={'query': query}
        )

        # The search result contains some info about itself
        # (this is not exhaustive)
        self.assertFalse(search_result['timed_out'])
        self.assertEqual(
            {'total': 5, 'successful': 5, 'failed': 0},
            search_result['_shards'])

        assert "hits" in search_result
        assert "total" in search_result['hits']
        assert "max_score" in search_result['hits']
        assert "hits" in search_result['hits']  # Where the actual hits live

        # "Camp Grenada" comes first because it has more hellos
        self.assertEqual(2, search_result['hits']['total'])
        self.assertEqual(post_2, search_result['hits']['hits'][0]['_source'])
        self.assertEqual(post_1, search_result['hits']['hits'][1]['_source'])

        # We can search by field, too
        query = {
            'term': {            # Search for a given term
                'title': 'hello'  # in any field (_all is a special wildcard)
            }
        }

        search_result = self.client.search(
            index="blog",
            doc_type="post",
            body={'query': query}
        )

        self.assertEqual(1, search_result['hits']['total'])
        self.assertEqual(post_1, search_result['hits']['hits'][0]['_source'])

if __name__ == "__main__":
    main()
