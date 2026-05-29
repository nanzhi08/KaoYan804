"""
Batch script to pre-generate AI explanations for all leaf knowledge points.
Usage: python scripts/batch_generate_explanations.py [--provider deepseek]
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import async_session
from app.models.knowledge_point import KnowledgePoint
from app.services.ai_service import build_explain_prompt, SYSTEM_PROMPT, _ensure_message_ids, get_provider
from sqlalchemy import select


async def get_leaf_ids(session):
    all_result = await session.execute(select(KnowledgePoint.id))
    all_ids = set(r[0] for r in all_result.all())

    parent_result = await session.execute(
        select(KnowledgePoint.parent_id).where(
            KnowledgePoint.parent_id.isnot(None)
        ).distinct()
    )
    parent_ids = set(r[0] for r in parent_result.all())

    return sorted(all_ids - parent_ids)


async def main(provider_name="deepseek"):
    provider = get_provider(provider_name)

    async with async_session() as session:
        leaf_ids = await get_leaf_ids(session)
        print(f"Found {len(leaf_ids)} leaf knowledge points.\n")

        success = 0
        for i, kp_id in enumerate(leaf_ids, 1):
            try:
                prompt = await build_explain_prompt(session, kp_id)
                messages = _ensure_message_ids([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ])
                print(f"[{i}/{len(leaf_ids)}] Generating explanation for KP #{kp_id}...", end=" ", flush=True)
                full_text = await provider.chat(messages)

                kp_result = await session.execute(
                    select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
                )
                kp = kp_result.scalar_one_or_none()
                if kp:
                    kp.ai_explanation = full_text
                    await session.commit()
                    print(f"Saved ({len(full_text)} chars)")
                    success += 1
                else:
                    print("KP not found, skipping")
            except Exception as e:
                print(f"ERROR: {e}")
                await session.rollback()

        print(f"\nDone. {success}/{len(leaf_ids)} explanations generated.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch generate AI explanations for leaf knowledge points")
    parser.add_argument("--provider", default="deepseek", help="AI provider name")
    args = parser.parse_args()
    asyncio.run(main(args.provider))
