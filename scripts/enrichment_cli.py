#!/usr/bin/env python3
"""
Command-Line Interface for FARFAN Enrichment System

Provides CLI commands for enrichment operations, validation, and management.
"""

import sys
import json
import click
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add parent to path


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """FARFAN Enrichment System CLI - Manage PDET context enrichment."""
    pass


@cli.command()
@click.option("--consumer-id", required=True, help="Consumer identifier")
@click.option("--policy-areas", required=True, help="Comma-separated policy areas (e.g., PA01,PA02)")
@click.option("--contexts", required=True, help="Comma-separated context types (e.g., municipalities,subregions)")
@click.option("--output", "-o", help="Output file path (JSON)")
@click.option("--strict/--no-strict", default=True, help="Strict mode (all gates must pass)")
def enrich(consumer_id, policy_areas, contexts, output, strict):
    """Perform enrichment operation."""
    try:
        from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
            EnrichmentOrchestrator,
            EnrichmentRequest,
        )
        from canonic_questionnaire_central.validations.runtime_validators import (
            SignalScope,
            ScopeLevel,
            SignalCapability,
        )
        
        # Parse inputs
        pas = [pa.strip() for pa in policy_areas.split(",")]
        ctx_types = [c.strip() for c in contexts.split(",")]
        
        # Create scope
        scope = SignalScope(
            scope_name=f"CLI_{consumer_id}",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=pas,
            min_confidence=0.50,
            max_signals_per_query=100
        )
        
        # Create orchestrator
        orchestrator = EnrichmentOrchestrator(strict_mode=strict)
        
        # Create request
        request = EnrichmentRequest(
            consumer_id=consumer_id,
            consumer_scope=scope,
            consumer_capabilities=[
                SignalCapability.SEMANTIC_PROCESSING,
                SignalCapability.TABLE_PARSING
            ],
            target_policy_areas=pas,
            target_questions=["Q001"],
            requested_context=ctx_types
        )
        
        # Perform enrichment
        click.echo(f"🔄 Enriching for consumer: {consumer_id}")
        click.echo(f"   Policy areas: {', '.join(pas)}")
        click.echo(f"   Contexts: {', '.join(ctx_types)}")
        
        result = orchestrator.enrich(request)
        
        if result.success:
            click.echo(f"✅ Enrichment successful!")
            click.echo(f"   Request ID: {result.request_id}")
            
            if output:
                output_path = Path(output)
                with open(output_path, "w") as f:
                    json.dump(result.enriched_data, f, indent=2, default=str)
                click.echo(f"   Output saved to: {output_path}")
            else:
                click.echo(f"   Data keys: {list(result.enriched_data.get('data', {}).keys())}")
        else:
            click.echo(f"❌ Enrichment failed!")
            for violation in result.violations:
                click.echo(f"   • {violation}")
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_providers():
    """List available context providers."""
    try:
        from canonic_questionnaire_central.colombia_context.context_providers import get_context_factory
        
        factory = get_context_factory()
        providers = factory.list_providers()
        
        click.echo("📋 Available Context Providers:")
        for provider in providers:
            click.echo(f"\n  • {provider['name']}")
            click.echo(f"    Supported contexts: {', '.join(provider['supported_contexts'])}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--format", "-f", type=click.Choice(["json", "csv"]), default="json", help="Export format")
@click.option("--output", "-o", required=True, help="Output file path")
def export_audit(format, output):
    """Export audit trail."""
    try:
        from canonic_questionnaire_central.validations.audit_trail import get_audit_manager
        
        audit_mgr = get_audit_manager()
        trail = audit_mgr.get_or_create_trail("enrichment_operations")
        
        output_path = Path(output)
        trail.export_to_file(output_path, format=format)
        
        click.echo(f"✅ Audit trail exported to: {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def verify_audit():
    """Verify audit trail integrity."""
    try:
        from canonic_questionnaire_central.validations.audit_trail import get_audit_manager
        
        audit_mgr = get_audit_manager()
        trail = audit_mgr.get_or_create_trail("enrichment_operations")
        
        click.echo("🔍 Verifying audit trail...")
        is_valid = trail.verify_chain()
        
        if is_valid:
            click.echo("✅ Audit trail is valid and unmodified")
        else:
            click.echo("❌ Audit trail has been tampered with!")
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def stats():
    """Show enrichment statistics."""
    try:
        from canonic_questionnaire_central.validations.audit_trail import get_audit_manager
        
        audit_mgr = get_audit_manager()
        trail = audit_mgr.get_or_create_trail("enrichment_operations")
        
        stats = trail.get_statistics()
        
        click.echo("📊 Enrichment Statistics:")
        click.echo(f"\n  Total operations: {stats['total_entries']}")
        click.echo(f"  Successful: {stats['successful_entries']}")
        click.echo(f"  Failed: {stats['failed_entries']}")
        click.echo(f"  Success rate: {stats['success_rate']:.1%}")
        
        if stats['total_entries'] > 0:
            click.echo(f"\n  Avg execution time: {stats['avg_execution_time']:.2f}s")
            click.echo(f"  Min execution time: {stats['min_execution_time']:.2f}s")
            click.echo(f"  Max execution time: {stats['max_execution_time']:.2f}s")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def load_config(config_file):
    """Load configuration from file."""
    try:
        from canonic_questionnaire_central.validations.configuration import get_config_manager
        
        config_path = Path(config_file)
        config_mgr = get_config_manager()
        config = config_mgr.load_config(config_path)
        
        click.echo(f"✅ Configuration loaded from: {config_path}")
        click.echo(f"\n  Version: {config.version}")
        click.echo(f"  Strict mode: {config.strict_mode}")
        click.echo(f"  All gates enabled: {config.enable_all_gates}")
        click.echo(f"  Async enabled: {config.async_enabled}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
