class BaseHandler:
    schema_class = None

    def _build_parsed_message(self, message):
        return self.schema_class(**message)

    def _get_message_argument_name(self):
        schema_name = self.schema_class.__name__.lower()
        return schema_name

    def handle(self, event, message):
        parsed_message = self._build_parsed_message(message)
        message_arg_name = self._get_message_argument_name()

        try:
            action_method = getattr(self, f"process_{event['event_action']}")
        except AttributeError:
            raise NotImplementedError()

        return action_method(**{"event": event, message_arg_name: parsed_message})
