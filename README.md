# JARVIS

A local-first personal AI computer assistant.

## Philosophy

JARVIS is designed to operate primarily on the user's own computer.

Core functionality should not depend on cloud LLM APIs.

External APIs may be used for features where an online service is appropriate, but the core assistant must remain functional without them.

## Hardware Target

CPU: Intel Core i7-12700H
RAM: 16 GB DDR4
GPU: Intel Iris Xe Graphics
OS: Windows x64

## Development Principles

- Build incrementally.
- Test every subsystem before integrating it.
- Prefer deterministic tools for deterministic tasks.
- Use the local LLM for reasoning rather than basic computer control.
- Keep components modular.
- Keep permissions explicit.
- Log important actions.
- Never silently perform dangerous actions.
- Maintain version history with Git.

## Current Status

Project initialization.

## Planned Systems

- Core runtime
- Command routing
- Computer control
- Voice
- Local LLM
- Vision
- Memory
- Knowledge / RAG
- Study assistant
- Developer assistant
- Research assistant
- Data analysis
- Agent system
- Learning and improvement
- Security and permissions
- GUI
- Background runtime
- Windows startup integration