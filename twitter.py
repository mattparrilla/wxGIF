from twython import Twython
from config import APP_KEY, APP_SECRET


def obtain_auth_url():
    """Used to app to tweet to my account
    NOT CALLED ANYWHERE"""
    twitter = Twython(APP_KEY, APP_SECRET)
    auth = twitter.get_authentication_tokens()

    oauth_token = auth['oauth_token']
    oauth_token_secret = auth['oauth_token_secret']
    print "\n\n\nGo to the following URL to authorize app:"
    print auth['auth_url']
    oauth_verifier = raw_input("\nEnter the pin: ")

    twitter = Twython(APP_KEY, APP_SECRET, oauth_token, oauth_token_secret)
    authorized = twitter.get_authorized_tokens(oauth_verifier)

    #write confirmed tokens to disk
    with open("config.py", "a") as config_file:
        config_file.write("\n'OAUTH_TOKEN': '" + authorized['oauth_token']
            + "'\n'OAUTH_TOKEN_SECRET': '" + authorized['oauth_token_secret'] + "'")

obtain_auth_url()
