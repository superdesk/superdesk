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
         "keywords": [{"relevance": "0.991938", "text": "Prime Minister Alexis"}, 
                      {"relevance": "0.906433", "text": "easier visa terms"}, 
                      {"relevance": "0.781422", "text": "re-energized consideration"}, 
                      {"relevance": "0.77959", "text": "EU Summit"}, 
                      {"relevance": "0.725234", "text": "EU leaders"}, 
                      {"relevance": "0.718816", "text": "Ankara cash"}, 
                      {"relevance": "0.664191", "text": "membership bid"}, 
                      {"relevance": "0.654447", "text": "national issues"}, 
                      {"relevance": "0.505621", "text": "Reuters"}, 
                      {"relevance": "0.478386", "text": "Brussels"}, 
                      {"relevance": "0.47406", "text": "migration"}, 
                      {"relevance": "0.473135", "text": "ATHENS"}, 
                      {"relevance": "0.472956", "text": "Friday"}, 
                      {"relevance": "0.454427", "text": "Turkey"}, 
                      {"relevance": "0.438753", "text": "Greece"}
                   ]
         }
        """