"""
Unit and Integration Tests for the 70-Node Jyotiṣa Decision & Interpretation Ontology
====================================================================================
Validates all 70 nodes, sub-node trees, query modes, cross-domain couplings,
system priorities, and integration with MethodologyRouter & ProtocolRegistry.
"""

import os
import sys
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jyotisha_ontology import (
    JyotishaOntology,
    MASTER_ONTOLOGY_NODES,
    QUERY_MODES,
    CROSS_DOMAIN_COUPLINGS,
    OntologyNode,
    OntologyRoutingResult
)
from methodology_router import MethodologyRouter
from event_protocols import ProtocolRegistry
from grandmaster_synthesis_engine import GrandmasterSynthesisEngine

class TestJyotishaOntology(unittest.TestCase):
    
    def test_all_70_nodes_present(self):
        """Assert that all 70 nodes (0 to 70) exist with populated sub-nodes and factors."""
        self.assertEqual(len(MASTER_ONTOLOGY_NODES), 71)  # Node 0 to Node 70 = 71 nodes
        
        for node_id in range(71):
            self.assertIn(node_id, MASTER_ONTOLOGY_NODES, f"Missing Node {node_id}")
            node = MASTER_ONTOLOGY_NODES[node_id]
            self.assertIsInstance(node, OntologyNode)
            self.assertTrue(len(node.title) > 0)
            self.assertTrue(len(node.subnodes) > 0, f"Node {node_id} has empty subnodes")
            self.assertTrue(len(node.category) > 0)
            self.assertTrue(len(node.system_priority) > 0)

    def test_query_modes_coverage(self):
        """Assert that all 24 query modes in Node 70 are mapped and detectable."""
        self.assertEqual(len(QUERY_MODES), 24)
        
        # Test timing detection (70.4)
        mode_id, mode_name = JyotishaOntology.detect_query_mode("When will my business scale?")
        self.assertEqual(mode_id, "70.4")
        self.assertEqual(mode_name, "When")
        
        # Test why/root cause (70.2)
        mode_id, mode_name = JyotishaOntology.detect_query_mode("Why is my career blocked?")
        self.assertEqual(mode_id, "70.2")
        self.assertEqual(mode_name, "Why")
        
        # Test location (70.5)
        mode_id, mode_name = JyotishaOntology.detect_query_mode("Where should I move for my company?")
        self.assertEqual(mode_id, "70.5")
        self.assertEqual(mode_name, "Where")
        
        # Test avoid/traps (70.15)
        mode_id, mode_name = JyotishaOntology.detect_query_mode("What financial traps should I avoid?")
        self.assertEqual(mode_id, "70.15")
        self.assertEqual(mode_name, "What should I avoid")

    def test_cross_domain_couplings(self):
        """Assert that cross-domain vectors from Node 68 are accurately mapped and detected."""
        self.assertEqual(len(CROSS_DOMAIN_COUPLINGS), 30)
        
        # Network -> Business
        links = JyotishaOntology.detect_cross_domain("Will foreign network clients scale my B2B agency?")
        self.assertTrue(any("68.7" in link for link in links))
        
        # Foreign -> Career
        links = JyotishaOntology.detect_cross_domain("How will foreign relocation impact my career?")
        self.assertTrue(any("68.9" in link for link in links))

    def test_domain_specific_routing(self):
        """Test precise node routing across key astrological queries."""
        # 1. B2B Agency / Software Business -> Node 5
        res = JyotishaOntology.classify_question("Will my B2B automation agency succeed?")
        self.assertEqual(res.node_id, 5)
        self.assertIn(10, res.primary_houses)
        self.assertIn(7, res.primary_houses)
        self.assertIn("Mercury", res.primary_karakas)
        self.assertIn("D10", res.primary_vargas)
        self.assertIn("AmK", res.jaimini_factors)
        
        # 2. Marriage & Spouse -> Node 10 / Node 9
        res = JyotishaOntology.classify_question("What is the personality and profession of my future spouse?")
        self.assertEqual(res.node_id, 10)
        self.assertIn(7, res.primary_houses)
        self.assertIn("Venus", res.primary_karakas)
        self.assertIn("D9", res.primary_vargas)
        self.assertIn("DK", res.jaimini_factors)
        
        # 3. Foreign Settlement -> Node 20
        res = JyotishaOntology.classify_question("Will I get permanent settlement abroad and foreign visa?")
        self.assertEqual(res.node_id, 20)
        self.assertIn(12, res.primary_houses)
        self.assertIn(9, res.primary_houses)
        self.assertIn("Rahu", res.primary_karakas)
        
        # 4. Longevity & Ayurdaya -> Node 24
        res = JyotishaOntology.classify_question("What is my longevity and ayurdaya lifespan calculation?")
        self.assertEqual(res.node_id, 24)
        self.assertIn(8, res.primary_houses)
        self.assertIn("Saturn", res.primary_karakas)
        self.assertIn("D8", res.primary_vargas)
        
        # 5. Gemstone Safety -> Node 45
        res = JyotishaOntology.classify_question("Which gemstone or ratna is suitable for me?")
        self.assertEqual(res.node_id, 45)
        self.assertIn(1, res.primary_houses)
        self.assertIn(9, res.primary_houses)

    def test_methodology_router_integration(self):
        """Verify that MethodologyRouter enriches its output with the 70-node ontology."""
        route = MethodologyRouter.route_question("When will my business scale through high-ticket clients?")
        self.assertIn("ontology", route)
        onto = route["ontology"]
        self.assertEqual(onto["node_id"], 5)
        self.assertEqual(route["query_mode"], "When")
        self.assertIn("D10", route["required_vargas"])
        self.assertTrue(len(route["falsification_checks"]) >= 3)

    def test_protocol_registry_integration(self):
        """Verify that ProtocolRegistry seamlessly synthesizes protocols from the ontology."""
        # Query for a specialized topic not in standard legacy hardcoded protocols
        protocol = ProtocolRegistry.get_protocol("vastu_alignment")
        self.assertIsNotNone(protocol)
        self.assertTrue(len(protocol.primary_houses) > 0)
        self.assertTrue(len(protocol.primary_karakas) > 0)

    def test_grandmaster_synthesis_ontology_binding(self):
        """Verify GrandmasterSynthesisEngine displays ontology routing metadata."""
        dummy_chart = {
            "ascendant_sign": "Capricorn",
            "current_dasha": {"mahadasha": "Ketu", "antardasha": "Sun"}
        }
        reading = GrandmasterSynthesisEngine.synthesize_reading(
            dummy_chart,
            query_domain="BUSINESS_SCALE",
            query_text="Will my agency scale through US B2B outreach?"
        )
        self.assertIn("Ontology Node:", reading)
        self.assertIn("Query Mode:", reading)
        self.assertIn("System Priority:", reading)

if __name__ == "__main__":
    unittest.main()
