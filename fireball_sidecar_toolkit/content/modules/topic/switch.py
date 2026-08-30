"""Switch the active topic, auto-saving any active chat first. Backs `/topic switch`.

Fuzzy-match confirmation ported from `fireball_ai_vault`'s `template_ai_vault` lineage
(2026-08-09) — a typo'd path now offers to switch to the closest match interactively
(`click.confirm`) instead of just naming it in an error and exiting. Everything else here predates
that port and stays as-is: auto-closing (not just noting) an active chat in the outgoing topic,
and `topic/active.py`'s own richer `active_topic.yml` schema (ported the same day) is what
actually records the switch.
"""

from __future__ import annotations

import difflib
import logging

from ..chat import active as chat_active
from ..chat import end as chat_end
from ..common import cli as click
from ..common.utils import error, info, success
from ..setup.properties import get_repo_root
from . import active as topic_active
from . import update_list

LOGGER = logging.getLogger(__name__)


def _suggest(topic_path: str) -> str | None:
    matches = difflib.get_close_matches(topic_path, update_list.list_topics(), n=1)
    return matches[0] if matches else None


@click.command()
@click.option("--path", required=True, help="Topic path to switch to, relative to topics/")
def main(path: str) -> None:
    """Switch the active topic to `path`, auto-saving any chat active in the outgoing topic."""
    current = topic_active.get_active_topic()
    if current is not None:
        current_dir = get_repo_root() / "topics" / current
        if chat_active.get_active_chat(current_dir) is not None:
            chat_end.auto_close(current_dir)
            info(f"Auto-saved the active chat in '{current}'")

    if not update_list.topic_exists(path):
        suggestion = _suggest(path)
        if suggestion and click.confirm(f"Topic '{path}' not found. Use '{suggestion}' instead?", default=True):
            path = suggestion
        elif suggestion:
            error(f"Run `/topic new {path}` to create it instead.")
        else:
            error(f"Topic '{path}' not found. Run `/topic new {path}` to create it.")

    topic_active.set_active_topic(path)
    success(f"Switched to: {path}")

    topic_dir = get_repo_root() / "topics" / path
    click.echo(f"Full path: {topic_dir}")
    click.echo(f"Instructions: {topic_dir / 'AGENTS.md'}")

    active_chat = chat_active.get_active_chat(topic_dir)
    if active_chat is not None:
        info(f"Resuming active chat: {active_chat.get('filename')} ({active_chat.get('title')})")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
