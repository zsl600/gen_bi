import boto3
import time

class NerveLog:
 
    # init method or constructor
    def __init__(self, log_group: str, log_stream:str):
        self.cloudwatch = boto3.client('logs')
        self.log_group = log_group
        self.log_stream = log_stream
        self.create_log_stream()

    def has_log_stream(self) -> bool:
        response = self.cloudwatch.describe_log_streams(
            logGroupName=self.log_group,
            logStreamNamePrefix=self.log_stream,
        )
        if len(response['logStreams']) > 0:
            return True
        else:
            return False
 
    def create_log_stream(self) -> str:
        response = self.has_log_stream()
        if response is True:
            return ""
        else:
            self.cloudwatch.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            return ""
        
    def write_log_event(self, event: str):
        # Add a record without a token (i.e. this is the first record.)
        response = self.cloudwatch.put_log_events(
            logGroupName=self.log_group,
            logStreamName=self.log_stream,
            logEvents=[
                {
                    "timestamp": int(round(time.time() * 1000)),
                    "message": event
                }
            ]
        )