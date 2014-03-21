require 'elasticsearch'

describe Elasticsearch do
  it "can connect to an elasticsearch server" do
    # Non-java clients connect to Elasticsearch via the REST api,
    # which runs on port 9200 by default.
    client = Elasticsearch::Client.new({
      host: 'localhost',
      port: 9200
    })
  end

  it "can add arbitrary documents to the index" do
    client = Elasticsearch::Client.new

    # Elasticsearch can store arbitrary documents
    post = {
      title: "My Document",
      body: "Hello world."
    }

    # Documents in elasticsearch have an INDEX and a
    # TYPE. You can also specify an ID here if you
    # want to generate your own.
    client.index({
      index: "blog",  # Think "database"
      type: "post",   # Think "table"
      body: post
    })
  end

  describe "search" do
    let(:post_1) do
      {
        "title" => "Hello World",
        "body" => "This is a post"
      }
    end


    let(:post_2) do
      {
        "title" => "Camp Grenada",
        "body" => "Hello mother, hello father."
      }
    end

    before(:each) do

      @client = Elasticsearch::Client.new

      # Drop the whole blog index for testing purposes
      @client.delete_by_query index: "blog", body: {query: {"match_all" => {}}}

      [post_1, post_2].each do |post|
        @client.index index: "blog", type: "post", body: post
      end

      # If the index is not refreshed, we won't find our documents right away.
      @client.perform_request "POST", "/blog/_refresh"
    end

    it "returns both results when searching for 'hello'" do
      query = {
        term: {          # Search for a given term
          _all: "hello"  # in any field (_all is a special wildcard)
        }
      }

      search_result = @client.search({
        index: "blog",
        type: "post",
        body: {query: query}
      })

      # The search result contains some info about itself (this is not exhaustive)
      search_result.should include({
        "timed_out" => false,
        "_shards" => {
          "total" => 5,
          "successful" => 5,
          "failed" => 0
        },
      })

      # The search hits are in "hits"
      search_result.should include "hits"

      # "hits" contains some metadata
      search_result["hits"].should include(
        "total", "max_score", "hits"
      )

      # "Camp Grenada" comes first because it has more hellos
      search_result["hits"]["total"].should eq(2)
      search_result["hits"]["hits"][0]["_source"].should eq(post_2)
      search_result["hits"]["hits"][1]["_source"].should eq(post_1)
    end

    it "returns one result when searching for 'Hello' in the title" do
      query = {
        term: {           # Search for a given term
          title: "hello"  # in the title
        }
      }

      search_result = @client.search({
        index: "blog",
        type: "post",
        body: {query: query}
      })

      search_result["hits"]["total"].should eq(1)
    end
  end
end
