"""
GraphMERT - Neurosymbolic Knowledge Graph Constructor

Compiles CharacterProfile data into a structured knowledge graph
for the Digital Person's "Active Mind" stored in Convex.
"""
from .compiler import GraphMERTCompiler, FactTriple, GraphMERTData

__all__ = [
    'GraphMERTCompiler',
    'FactTriple',
    'GraphMERTData'
]
