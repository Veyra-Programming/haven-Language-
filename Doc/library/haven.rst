.. _haven:

==================================================
The Haven Programming Language & ODCS Architecture
==================================================

Haven is a modern, high-concurrency, developer-friendly programming language designed
from the ground up for the Open Digital Continuity Standard (ODCS) by Anirudha Puthraya.

Core Architecture
=================

* **Pipelined Dataflow**: Left-to-right processing via ``|>`` and ``into``.
* **ODCS Continuity Primitives**: Native syntax for ``durable record``, ``checkpoint``, and ``verify``.
* **Natural English Constructs**: Conversational programming using ``set ... to``, ``unless``, ``until``, ``repeat N times``, and ``function ...``.
* **Integrated AI SDK**: Native ``haven_ai`` client with built-in pipeline chaining.
