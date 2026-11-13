"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    ids = {source['id'] for source in data['sources']}
    findings = await agent.ask('findings', 'Extract one supported finding per source; keep the source_id field.', data,
                               {'claims': [{'text': source['text'], 'source_id': source['id']} for source in data['sources']]})
    if any(claim['source_id'] not in ids for claim in findings['claims']):
        raise ValueError('Finding cites an unknown source')
    report = await agent.ask('report', 'Write a brief with bracketed source IDs after factual claims.', findings,
                             '\n'.join(claim['text'] + ' [' + claim['source_id'] + ']' for claim in findings['claims']))
    return {'findings': findings, 'report': report, 'citation_coverage': all('[' + sid + ']' in report for sid in ids)}
