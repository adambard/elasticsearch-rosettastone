<?php
require 'vendor/autoload.php';

# Non-java clients connect to Elasticsearch via the REST api,
# which runs on port 9200 by default."""
$client = new Elasticsearch\Client(array(
    'hosts' => ['localhost:9200']
));


# Elasticsearch can store arbitrary documents
$post = array(
    "title" => "My Document",
    "body" => "Hello world."
);

# Documents in elasticsearch have an INDEX and a
# TYPE. You can also specify an ID here if you
# want to generate your own.
$client->index(array(
    'index' => 'blog',  # Think "database"
    'type' => "post",  # Think "table"
    'body' => $post
));

# Delete that post
$client->deleteByQuery(array(
    "index" => "blog",
    "body" => array(
      'query' => array(
        "match_all" => array()))));


$post_1 = array(
    "title" => "Hello World",
    "body" => "This is a post"
);

$post_2 = array(
    "title" => "Camp Grenada",
    "body" => "Hello mother, hello father."
);

# Index those documents
$client->index(array(
    'index' => 'blog',
    'type' => "post",
    'body' => $post_1));

$client->index(array(
    'index' => 'blog',
    'type' => "post",
    'body' => $post_2));

# If the index is not refreshed, we won't find our documents
# right away.
$client->indices()->refresh(array("index" => "blog"));

$query = array(
    'term' => array(            # Search for a given term
        '_all' => 'hello'  # in any field (_all is a special wildcard)
    )
);

$search_result = $client->search(array(
    "index" => "blog",
    "type" => "post",
    "body" => array('query' => $query)
));

# The search result contains some info about itself
# (this is not exhaustive)
assert(!$search_result['timed_out']);

assert($search_result['_shards']['total'] === 5);
assert($search_result['_shards']['successful'] === 5);
assert($search_result['_shards']['failed'] === 0);

assert($search_result["hits"]);

assert($search_result["hits"]["total"] === 2);
assert($search_result["hits"]["hits"][0]['_source'] == $post_2);
assert($search_result["hits"]["hits"][1]['_source'] == $post_1);

echo "Ok.\n";
