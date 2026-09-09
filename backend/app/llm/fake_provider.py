from __future__ import annotations

import json


class FakeProvider:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        draft = user_prompt.split("DRAFT TO ANALYZE:", 1)[-1].strip()
        excerpt = draft[:140].rstrip(".")
        return json.dumps(
            {
                "assessment": {
                    "tone": "Clear and informative",
                    "newsworthiness_score": 72,
                    "newsworthiness_summary": "The announcement has a concrete update with several possible editorial hooks.",
                    "strengths": ["A clear announcement", "A specific audience impact"],
                    "risks": ["The strongest claims need evidence"],
                    "missing_context": ["Add a named spokesperson or supporting data"],
                },
                "pitches": [
                    {
                        "angle": "tech_product",
                        "angle_label": "Tech / Product",
                        "subject": "A practical product story behind the announcement",
                        "body": f"Hi there,\\n\\nI thought this product update might be relevant to your readers. {excerpt}. The story offers a look at how the product is being developed and used.\\n\\nBest,\\nPressPulse AI",
                        "personalization_guidance": "Lead with the product change and its practical user impact.",
                        "story_hook": "A product update with a clear use case.",
                    },
                    {
                        "angle": "business_founder",
                        "angle_label": "Business / Founder",
                        "subject": "The company strategy behind a timely launch",
                        "body": f"Hi there,\\n\\nI am sharing a business angle on the announcement: {excerpt}. It could support a conversation about the company's direction, market context, and the people building it.\\n\\nBest,\\nPressPulse AI",
                        "personalization_guidance": "Connect the announcement to company strategy and leadership context.",
                        "story_hook": "The business decision and people behind the launch.",
                    },
                    {
                        "angle": "local_human_interest",
                        "angle_label": "Local / Human Interest",
                        "subject": "A local story about people affected by the announcement",
                        "body": f"Hi there,\\n\\nThere may be a local and human story in this announcement: {excerpt}. The team can speak about the people, place, and practical change behind the news.\\n\\nBest,\\nPressPulse AI",
                        "personalization_guidance": "Add a local person, place, or community outcome before pitching this angle.",
                        "story_hook": "The human and local impact behind the announcement.",
                    },
                ],
                "verification": {
                    "overall_risk": "low",
                    "summary": "Review the highlighted claims and add evidence before sending.",
                    "claims": [],
                },
                "warnings": [],
            }
        )
