import uuid


class BaseHandler:
    schema_class = None

    def _build_action_kwargs(self, metadata, message):
        kwargs = {"metadata": metadata}
        schema_name = metadata.event_schema

        if metadata.event_action == "deleted":
            kwargs[f"{schema_name}_id"] = uuid.UUID(message[0])
        elif metadata.event_action == "removed":
            kwargs["parent_id"] = uuid.UUID(message[0])
            kwargs[f"{schema_name}_id"] = uuid.UUID(message[1])
        else:
            kwargs[schema_name] = self.schema_class.build_from_message(message)

        return kwargs

    def handle(self, metadata, message):
        try:
            action_method = getattr(self, f"process_{metadata.event_action}")
        except AttributeError:
            raise NotImplementedError()

        return action_method(**self._build_action_kwargs(metadata, message))
