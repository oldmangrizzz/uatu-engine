#!/usr/bin/env python
"""
Demonstration of the Hybrid Mind Integration (Neural Bridge)

This script demonstrates the complete flow:
1. Input: Receive User Text
2. Filter: Pass to GraphMERT -> Get Triples
3. Feel: Update NeurotransmitterEngine
4. Think: Run DialecticInference
5. Act: Generate Output
6. Record: Log to Convex

Run this to see the Neural Bridge in action!
"""
import asyncio
from uatu_genesis_engine.agent_zero_integration import HybridMindIntegration


async def demonstrate_neural_bridge():
    """Demonstrate the complete Neural Bridge flow."""
    
    print("\n" + "=" * 80)
    print("NEURAL BRIDGE DEMONSTRATION")
    print("Completing the Hybrid Mind Architecture")
    print("=" * 80)
    
    # Sample soul anchor data (Lucius Fox persona)
    soul_anchor = {
        "archetype": "Tech Genius / Ethical Innovator",
        "core_constants": [
            "Innovation through ethical boundaries",
            "Technology as protective shield",
            "Mentor to the protector"
        ],
        "core_drive": "Create defensive technologies that protect without compromising principles"
    }
    
    print("\nInitializing Hybrid Mind Integration...")
    print(f"  Archetype: {soul_anchor['archetype']}")
    print(f"  Core Drive: {soul_anchor['core_drive']}")
    
    # Initialize the integration
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor)
    await mind.start()
    
    print("\n✓ All subsystems online:")
    print("  - GraphMERT (Truth Filter)")
    print("  - NeurotransmitterEngine (Digital Psyche)")
    print("  - DialecticInference (Cognitive Engine)")
    print("  - ConvexStateLogger (Black Box)")
    
    # Test scenarios
    scenarios = [
        {
            "input": "Lucius, I need help with the Wayne Enterprises security breach.",
            "description": "Security Incident Request"
        },
        {
            "input": "URGENT! Critical system hack! Need immediate assistance!",
            "description": "High-Urgency Emergency"
        },
        {
            "input": "How's the weather today?",
            "description": "Casual Conversation"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print("\n" + "=" * 80)
        print(f"SCENARIO {i}: {scenario['description']}")
        print("=" * 80)
        print(f"User Input: \"{scenario['input']}\"")
        print()
        
        # Process the input
        state = await mind.process_user_input(scenario['input'])
        
        # Display results
        print("\n--- RESULTS ---")
        
        # GraphMERT Triples
        if state.graphmert_response:
            print(f"\n[1] GraphMERT Truth Filter:")
            triples = state.graphmert_response['fact_triples']
            print(f"    Extracted {len(triples)} fact triple(s):")
            for triple in triples:
                print(f"      • ({triple['subject']}) -> [{triple['predicate']}] -> ({triple['object']})")
            print(f"    Toxicity: {state.graphmert_response['toxicity_score']:.2f}")
            print(f"    Urgency: {state.graphmert_response['urgency_score']:.2f}")
            print(f"    Intent: {state.graphmert_response['intent_detected']}")
        
        # Neurotransmitter State
        if state.neurotransmitter_state:
            print(f"\n[2] Neurotransmitter Engine (Digital Psyche):")
            nt = state.neurotransmitter_state
            print(f"    Dopamine:  {nt['dopamine']:.3f} (reward/anticipation)")
            print(f"    Serotonin: {nt['serotonin']:.3f} (stability/harmony)")
            print(f"    Cortisol:  {nt['cortisol']:.3f} (stress/threat)")
            
            if state.emotional_flags:
                flags = state.emotional_flags
                active_flags = [
                    flag for flag, value in flags.items() if value
                ]
                if active_flags:
                    print(f"    Active Flags: {', '.join(active_flags)}")
        
        # LLM Modifiers
        modifiers = mind.get_llm_modifiers()
        print(f"\n[3] LLM Parameter Modifiers:")
        print(f"    Temperature: {modifiers['temperature']} (creativity)")
        print(f"    Top-P: {modifiers['top_p']} (token selection)")
        
        # Dialectical Reasoning
        if state.dialectical_chain:
            print(f"\n[4] Dialectical Reasoning (Zord Theory):")
            chain = state.dialectical_chain
            print(f"    Thesis:     {chain['thesis']['content'][:80]}...")
            print(f"    Antithesis: {chain['antithesis']['content'][:80]}...")
            print(f"    Synthesis:  {chain['synthesis']['content'][:80]}...")
        
        # Metadata
        print(f"\n[5] Processing Metadata:")
        print(f"    Processing Time: {state.processing_time_ms:.2f}ms")
        print(f"    Logged to Convex: {'Yes' if state.subsystems_enabled['convex'] else 'No'}")
        
        print()
    
    # Final statistics
    print("\n" + "=" * 80)
    print("SESSION STATISTICS")
    print("=" * 80)
    
    stats = mind.get_statistics()
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"\nSubsystems Status:")
    for system, enabled in stats['subsystems_enabled'].items():
        print(f"  {system.capitalize()}: {'ENABLED' if enabled else 'DISABLED'}")
    
    if 'graphmert_stats' in stats:
        gm_stats = stats['graphmert_stats']
        print(f"\nGraphMERT Statistics:")
        print(f"  Total Requests: {gm_stats['total_requests']}")
        print(f"  Total Triples Extracted: {gm_stats['total_triples_extracted']}")
        print(f"  Avg Triples/Request: {gm_stats['average_triples_per_request']:.2f}")
    
    if 'convex_stats' in stats:
        cv_stats = stats['convex_stats']
        print(f"\nConvex Logger Statistics:")
        print(f"  Total Logged: {cv_stats['total_logged']}")
        print(f"  Total Flushed: {cv_stats['total_flushed']}")
        print(f"  Buffer Size: {cv_stats['buffer_size']}")
    
    # Shutdown
    print("\n" + "=" * 80)
    print("Shutting down subsystems...")
    await mind.stop()
    print("✓ All subsystems stopped cleanly")
    print("=" * 80)
    print("\n🎉 NEURAL BRIDGE DEMONSTRATION COMPLETE!")
    print("The Hybrid Mind is operational.\n")


if __name__ == "__main__":
    asyncio.run(demonstrate_neural_bridge())
