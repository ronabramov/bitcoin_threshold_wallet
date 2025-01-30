import json

class Message:
    def __init__(self, content: str):
        self.content = content

    def serialize(self):
        return json.dumps(self.content)
    
    def deserialize(self, serialized_message: str):
        return json.loads(serialized_message)
    

class TransactionMessage(Message):
    def __init__(self, _content: str):
        super().__init__(_content)
    
    @property
    def content(self):
        return self.deserialize(self._content)







msk = TransactionMessage(getMessg())

