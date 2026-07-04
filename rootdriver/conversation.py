from .types import Message
from .utils import get_iso_timestamp, build_system_message


class Conversation:
    def __init__(self, system_prompt: str = None):
        self.messages: list[Message] = []
        self.system_prompt = system_prompt
        if self.system_prompt:
            self.append(build_system_message(system_prompt))

    def append(self, message: Message) -> "Conversation":
        self.messages.append(message)
        return self

    def append_many(self, messages: list[Message]) -> "Conversation":
        self.messages.extend(messages)
        return self

    # def append_user(self, content: str) -> "Conversation":
    #     self.messages.append(Message(role="user", content=content, created_at=get_iso_timestamp()))
    #     return self
    #
    # def append_assistant(self, content: str | None = None, tool_calls: list | None = None) -> "Conversation":
    #     msg = Message(role="assistant", content=content, created_at=get_iso_timestamp())
    #     if tool_calls:
    #         msg.tool_calls = tool_calls
    #     self.messages.append(msg)
    #     return self
    #
    # def append_tool(self, tool_call_id: str, content: str) -> "Conversation":
    #     self.messages.append(Message(
    #         role="tool",
    #         tool_call_id=tool_call_id,
    #         content=content,
    #         created_at=get_iso_timestamp()
    #     ))
    #     return self

    def append_system(self, content: str) -> "Conversation":
        self.messages.append(Message(role="system", content=content, created_at=get_iso_timestamp()))
        return self
    def update_message(self, messages: list[Message]) -> "Conversation":
        self.messages = messages.copy()
        return self

    def delete(self, index: int=-1) -> "Conversation":
        self.messages.pop(index)
        return self

    def get_messages(self) -> list[Message]:
        '''返回 list[message<obj>]'''
        return self.messages

    def get_messages_in_list(self) -> list[dict]:
        '''返回 字典加列表组成的message（可转成json用于网络、跨语言传输） 组成的列表'''
        return [m.model_dump(exclude_none=False) for m in self.messages]
    def get_message_by_index(self, index: int=-1) -> Message:
        return self.messages[index]
    def get_message_in_list_by_index(self, index:int=-1) -> list[dict]:
        """据索引返回当前消息列表的"""
        return self.messages[index].model_dump(exclude_none=False)
    @classmethod
    def from_dict_list(cls, messages: list[dict]) -> "Conversation":
        conv = cls()
        conv.messages = [Message.model_validate(m) for m in messages]
        return conv
    from_messages_to_conversation = from_dict_list
    @classmethod
    def from_list(cls, messages: list[Message]) -> "Conversation":
        conv = cls()
        conv.messages = list(messages)
        return conv
    from_messages_list_to_conversation = from_dict_list

    def clear(self) -> "Conversation":
        self.messages = []
        return self

    def copy(self) -> "Conversation":
        """返回当前 conversation 的浅拷贝"""
        new_conv = Conversation()
        new_conv.messages = list(self.messages)
        new_conv.system_prompt = self.system_prompt
        return new_conv

