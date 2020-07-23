import uuid

from . import stored_proposals
from .schemas import Proposal


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


class ProposalHandler(BaseHandler):
    schema_class = Proposal

    def process_created(self, metadata, proposal):
        proposal_id = proposal.proposal_id
        # idempotency to avoid overwrite
        if stored_proposals.get(proposal_id):
            return

        # store proposal
        stored_proposals[proposal_id] = proposal

    def process_updated(self, metadata, proposal):
        proposal_id = proposal.proposal_id
        current_proposal = stored_proposals.get(proposal_id)
        # cant updated if doesnt exists
        if not current_proposal:
            return

        # avoid overwrite relateds
        proposal.warranties = current_proposal.warranties
        proposal.proponents = current_proposal.proponents

        # update reference to updated obj
        stored_proposals[proposal_id] = proposal

    def process_deleted(sefl, metadata, proposal_id):
        # pop reference if exists
        stored_proposals.pop(proposal_id, None)
