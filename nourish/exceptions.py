class FacebookAuthTimeout(Exception):
    def __str__(self):
        return "facebook auth timed out"
