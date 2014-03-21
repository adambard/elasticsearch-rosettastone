var elasticsearch = require('elasticsearch');

// Non-java clients connect to Elasticsearch via the REST api,
// which runs on port 9200 by default.
var client = new elasticsearch.Client({
    host: 'localhost:9200'
});

// Elasticsearch can store arbitrary documents
post = {
    title: "My Document",
    body: "Hello world."
};

// Documents in elasticsearch have an INDEX and a
// TYPE. You can also specify an ID here if you
// want to generate your own.
client.index({
    index: "blog",  // Think "database"
    type: "post",   // Think "table"
    body: post
}).then(function(){
    // Drop the whole blog index for testing purposes
    return client.deleteByQuery({
      index: "blog",
      body: {query: {"match_all": {}}}
    });
}).then(function(){
    post_1 = {
        "title": "Hello World",
        "body": "This is a post"
    };

    return client.index({index: "blog", type: "post", body: post_1});
}).then(function(){
    post_2 = {
        "title": "Camp Grenada",
        "body": "Hello mother, hello father."
    };
    return client.index({index: "blog", type: "post", body: post_2});
}).then(function(){
    // If the index is not refreshed, we won't find our documents right away.
    return client.indices.refresh({index: "blog"});
}).then(function(){

    query = {
        term: {          // Search for a given term
            _all: "hello"  // in any field (_all is a special wildcard)
        }
    };

    returned = 0;
    return client.search({
        index: "blog",
        type: "post",
        body: {query: query}
    });
}).then(function(search_result){

    console.assert(!search_result.timed_out);

    console.assert(search_result._shards.total === 5);
    console.assert(search_result._shards.successful === 5);
    console.assert(search_result._shards.failed === 0);

    console.assert(search_result.hits.total === 2);
    actual = search_result.hits.hits[0]._source;
    console.assert(actual.title == post_2.title);
    console.assert(actual.body == post_2.body);

    actual = search_result.hits.hits[1]._source;
    console.assert(actual.title == post_1.title);
    console.assert(actual.body == post_1.body);
}).then(function(){
    query = {
        term: {           // Search for a given term
            title: "hello"  // in the title
        }
    };

    return client.search({
        index: "blog",
        type: "post",
        body: {query: query}
    });
}).then(function(search_result){
    console.assert(search_result.hits.total === 1);
    console.log("Ok.");
}, function(e){
    console.log("FAILED");
});
