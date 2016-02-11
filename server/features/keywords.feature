Feature: Keywords

    @auth
    Scenario: Get the list of keywords for a content item
        When we post to "/keywords"
        """
        {
         "text": "ATHENS (Reuters) - Greece is willing to support Turkey over migration but will not compromise on national issues, Prime Minister Alexis Tsipras said on Friday after attending an EU Summit in Brussels. EU leaders agreed overnight to offer Ankara cash, easier visa terms and a re-energized consideration of Turkey's membership bid."
        }
        """
        Then we get existing resource
        """
        {"_id": 0,
         "keywords": [{"relevance": "0.943564", "text": "Prime Minister Alexis Tsipras"}, 
                      {"relevance": "0.915151", "text": "EU"}, 
                      {"relevance": "0.775952", "text": "Turkey"}, 
                      {"relevance": "0.542216", "text": "Reuters"}, 
                      {"relevance": "0.490861", "text": "ATHENS"}, 
                      {"relevance": "0.47575", "text": "Brussels"}, 
                      {"relevance": "0.458178", "text": "Ankara"}, 
                      {"relevance": "0.455677", "text": "Greece"}
                   ]
         }
        """
