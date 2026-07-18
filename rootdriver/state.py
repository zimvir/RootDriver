from .conversation_repo import ConversationRepo


class State(ConversationRepo):
    def __init__(self,conversation_repo:ConversationRepo):
        self.conversation_repo = conversation_repo

