import uuid

from .exceptions import ReferenceDoesNotExist
from .schemas import Proponent, Proposal, Warranty


class BaseHandler:
    schema_class = None

    def __init__(self, stored_proposals):
        self.stored_proposals = stored_proposals

    def _get_stored_proposal(self, proposal_id):
        try:
            return self.stored_proposals[proposal_id]
        except KeyError:
            raise ReferenceDoesNotExist(f"proposal_id={proposal_id}")

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
        if self.stored_proposals.get(proposal_id):
            return

        # store proposal
        self.stored_proposals[proposal_id] = proposal

    def process_updated(self, metadata, proposal):
        proposal_id = proposal.proposal_id
        current_proposal = self.stored_proposals.get(proposal_id)
        # cant updated if doesnt exists
        if not current_proposal:
            return

        # avoid overwrite relateds
        proposal.warranties = current_proposal.warranties
        proposal.proponents = current_proposal.proponents

        # update reference to updated obj
        self.stored_proposals[proposal_id] = proposal

    def process_deleted(self, metadata, proposal_id):
        # pop reference if exists
        self.stored_proposals.pop(proposal_id, None)


class ProponentHandler(BaseHandler):
    schema_class = Proponent

    def process_added(self, metadata, proponent):
        proponent_id = proponent.proponent_id
        proposal = self._get_stored_proposal(proponent.proposal_id)
        # idempotency to avoid overwrite
        if proposal.proponents.get(proponent_id):
            return

        # store proponent
        proposal.proponents[proponent_id] = proponent

    def process_updated(self, metadata, proponent):
        proponent_id = proponent.proponent_id
        proposal = self._get_stored_proposal(proponent.proposal_id)

        # update reference to updated obj
        proposal.proponents.update({proponent_id: proponent})

    def process_removed(self, metadata, parent_id, proponent_id):
        proposal = self._get_stored_proposal(parent_id)
        # pop reference if exist
        proposal.proponents.pop(proponent_id, None)


class WarrantyHandler(BaseHandler):
    schema_class = Warranty

    def process_added(self, metadata, warranty):
        warranty_id = warranty.warranty_id
        proposal = self._get_stored_proposal(warranty.proposal_id)
        # idempotency to avoid overwrite
        if proposal.warranties.get(warranty_id):
            return

        # store warranty
        proposal.warranties[warranty_id] = warranty

    def process_updated(self, metadata, warranty):
        warranty_id = warranty.warranty_id
        proposal = self._get_stored_proposal(warranty.proposal_id)

        # update reference to updated obj
        proposal.warranties.update({warranty_id: warranty})

    def process_removed(self, metadata, parent_id, warranty_id):
        proposal = self._get_stored_proposal(parent_id)
        # pop reference if exist
        proposal.warranties.pop(warranty_id, None)
