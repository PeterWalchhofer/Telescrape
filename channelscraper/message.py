from utilities import getClassName


class Message:
    def __init__(self):
        self.text = ""
        self.id = None
        self.timestamp = None
        self.replyToMessageId = ""
        self.views = None
        self.sender = None
        self.replyToMessageId = ""
        self.edit_date = None
        self.entities = list()
        self.forward = None
        self.forwardId = None
        self.forward_msg_id = None
        self.forward_msg_date = None
        self.post_author = None
        self.comments = []
        self.sender_name = None
        self.username = None
        self.urls = None
        self.media = None
        self.isComment = False
        self.hasComments = False
        self.parent = None
        self.bot_url = None
        self.isDeleted = ""
        self.bot_url = None

    @staticmethod
    def getMessageHeader():
        return ["channel", "member_count", "broadcast", "id", "timestamp", "content", "user_id", "first_and_last_name",
                "username",
                "views", "edit-date",
                "replyToId", "forward", "forward_id", "forward_msg_id", "forward_date", "URLs", "media", "hasComments",
                "isComment",
                "bot_url",
                "parent", "isDeleted"]

    @staticmethod
    def getUserHeader():
        return ["channel", "Id", "first_name", "last_name", "first_and_last_name", "phone", "bot",
                "verified",
                "username"]

    def getMessageRow(self, channel_username, channel_member_count, channel_broadcast):
        row = [channel_username, channel_member_count, channel_broadcast, self.id, self.timestamp, self.text,
               self.sender,
               self.sender_name,
               self.username, self.views,
               self.edit_date, self.replyToMessageId, self.forward, self.forwardId, self.forward_msg_id,
               self.forward_msg_date,
               ", ".join(self.urls),
               getClassName(self.media), self.hasComments, self.isComment, self.bot_url,
               self.parent, self.isDeleted]
        return row
