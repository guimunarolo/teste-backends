class BaseHandler:
    schema_class = None

    def process(self, **kwargs):
        raise NotImplementedError()

    def handle(self, event, message):
        parsed_message = self.schema_class(**message)
        message_arg_name = self.schema_class.__name__.lower()

        self.process(**{"event": event, message_arg_name: parsed_message})
