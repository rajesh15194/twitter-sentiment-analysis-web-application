import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
  

from flask import Flask, render_template, request,jsonify,json
app = Flask(__name__)


class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = ''
        consumer_secret = ''
        access_token = ''
        access_token_secret = ''
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 
  
    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
  
    def get_tweet_sentiment(self, tweet): 
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'
  
    def get_tweets(self, query, count = 10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 
  
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
  
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            # return parsed tweets 
            return tweets 
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 
            
            
@app.route('/')
def main():
    return render_template('home.html')

@app.route('/process', methods=['POST'])
def process():
    hashtag = request.form['hashtag']
        # Validate and send response
    if hashtag:
        #hashtag="test"
        print("hashtag---",hashtag)
        # creating object of TwitterClient Class 
        api = TwitterClient() 
        # calling function to get tweets 
        tweets = api.get_tweets(query = hashtag, count = 200) 
        twitterData= [tweet for tweet in tweets [:10] ] 
        # picking positive tweets from tweets 
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
        # percentage of positive tweets 
        pospercent=100*(len(ptweets)/len(tweets))
        formatted_pospercent = "{:.2f}".format(pospercent)
        # picking negative tweets from tweets 
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
        # percentage of negative tweets 
        negpercent= 100*(len(ntweets)/len(tweets))
        formatted_negpercent = "{:.2f}".format(negpercent)
        # percentage of neutral tweets 
        neupercent=100*((len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))
        formatted_neupercent = "{:.2f}".format(neupercent)
        # printing first 5 positive tweets 
        for tweet in ptweets[:10]: 
            print(tweet['text']) 
            
       # t.append(positiveTweets)
        # printing first 5 negative tweets 
        for tweet in ntweets[:10]: 
            print(tweet['text']) 
        #t.append(negativeTweets)
        #print("T data---",t)
        dict = {'hashtag':hashtag,
                'percentage of positive tweets ':formatted_pospercent,
                'percentage of negative tweets':formatted_negpercent,
                'percentage of neutral tweets':formatted_neupercent,
                'tweet0':twitterData[0]['text'],
                'sentiment0':twitterData[0]['sentiment'],
                'tweet1':twitterData[1]['text'],
                'sentiment1':twitterData[1]['sentiment'],
                'tweet2':twitterData[2]['text'],
                'sentiment2':twitterData[2]['sentiment'],
                'tweet3':twitterData[3]['text'],
                'sentiment3':twitterData[3]['sentiment'],
                'tweet4':twitterData[4]['text'],
                'sentiment4':twitterData[4]['sentiment']}
        print("T data---",dict)
        #return "Welcome!"
        return render_template('j2_response.html', tweetData=dict)
    else:
        return 'Please go back and enter a search creteria', 400  # 400 Bad Request

  
if __name__ == '__main__':
    app.run(debug=True)
