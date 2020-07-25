from .handlers import ProponentHandler, ProposalHandler, WarrantyHandler
from .schemas import EventMetadata


class Dispatcher:
    def __init__(self):
        self.handlers = {
            "proponent": ProponentHandler,
            "proposal": ProposalHandler,
            "warranty": WarrantyHandler,
        }
        self.processed_events = []
        self.stored_proposals = {}

    def dispatch(self, raw_event):
        event_id, event_schema, event_action, event_timestamp, *message = raw_event.split(",")
        event_metadata = EventMetadata(
            event_id=event_id,
            event_schema=event_schema,
            event_action=event_action,
            event_timestamp=event_timestamp,
        )

        if event_id not in self.processed_events:
            try:
                SchemaHandler = self.handlers[event_schema]
            except KeyError:
                raise ValueError(f"Handler for {event_schema} not found!")
            else:
                SchemaHandler(self.stored_proposals).handle(event_metadata, message)
                self.processed_events.append(event_id)


def read_events(raw_events_string):
    dispatcher = Dispatcher()

    for raw_event in raw_events_string.split("\n"):
        if raw_event.strip() == "":
            continue

        # avoid events count line
        try:
            int(raw_event)
            continue
        except ValueError:
            pass

        dispatcher.dispatch(raw_event)

    valid_proposals = [
        str(proposal.proposal_id)
        for _, proposal in dispatcher.stored_proposals.items()
        if proposal.is_valid()
    ]

    return ",".join(valid_proposals)
