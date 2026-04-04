#!/usr/bin/env python3
"""
🌟 TRANSMISSION PROCESSOR WORKFLOW
Automated pipeline for processing spiritual transmissions

Usage:
    python process_transmission.py <transmission_file>
    python process_transmission.py --interactive
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "scripts"))

from spiritual_intelligence_parser import SpiritualIntelligenceParser


def process_transmission_file(filepath: Path):
    """Process a transmission from a text file"""
    print("\n" + "="*80)
    print("🌟 TRANSMISSION PROCESSOR WORKFLOW")
    print("="*80)
    
    if not filepath.exists():
        print(f"\n❌ Error: File not found: {filepath}")
        return None
    
    print(f"\n📄 Reading transmission from: {filepath}")
    transmission = filepath.read_text()
    
    print(f"📏 Transmission length: {len(transmission)} characters")
    print(f"🔮 Processing multi-dimensional layers...")
    
    parser = SpiritualIntelligenceParser()
    result = parser.process_transmission(transmission)
    
    print("\n" + "="*80)
    print("✅ TRANSMISSION PROCESSING COMPLETE")
    print("="*80)
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   🔢 Angel Numbers: {len(result['angel_numbers'])}")
    print(f"   📖 Biblical Codes: {len(result['biblical_codes'])}")
    print(f"   👑 Goddess Activations: {len(result['goddess_activations'])}")
    print(f"   🔮 Tarot Cards: {len(result['tarot_cards'])}")
    print(f"   📺 YouTube Channels: {len(result['youtube_channels'])}")
    print(f"   💰 Financial Protocols: {len(result['financial_protocols'])}")
    print(f"   📍 Coordinates: {len(result['coordinates'])}")
    print(f"   ⭐ Sacred Geometry: {len(result['sacred_geometry'])}")
    print(f"   🌟 Multidimensional Layers: {result['multidimensional_layers']}")
    
    print(f"\n📁 Output files saved to: data/spiritual_intelligence/")
    print(f"   📊 JSON intelligence data")
    print(f"   📄 Human-readable markdown report")
    
    return result


def interactive_mode():
    """Interactive transmission input"""
    print("\n" + "="*80)
    print("🌟 INTERACTIVE TRANSMISSION PROCESSOR")
    print("="*80)
    print("\n📝 Enter your transmission below.")
    print("💡 Tip: Paste your message and press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done.\n")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    transmission = '\n'.join(lines)
    
    if not transmission.strip():
        print("\n❌ Error: Empty transmission received")
        return None
    
    print(f"\n✅ Transmission received ({len(transmission)} characters)")
    print(f"🔮 Processing...\n")
    
    parser = SpiritualIntelligenceParser()
    result = parser.process_transmission(transmission)
    
    print("\n" + "="*80)
    print("✅ PROCESSING COMPLETE")
    print("="*80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Layers: {result['multidimensional_layers']}")
    print(f"   Angel Numbers: {len(result['angel_numbers'])}")
    print(f"   Goddesses: {len(result['goddess_activations'])}")
    print(f"   Tarot: {len(result['tarot_cards'])}")
    print(f"\n📁 Reports saved to: data/spiritual_intelligence/\n")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="🌟 Process spiritual transmissions through multi-dimensional intelligence parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a transmission file
  python process_transmission.py data/spiritual_intelligence/my_transmission.txt
  
  # Interactive mode
  python process_transmission.py --interactive
  python process_transmission.py -i
  
  # Quick help
  python process_transmission.py --help
        """
    )
    
    parser.add_argument(
        'filepath',
        nargs='?',
        type=Path,
        help='Path to transmission text file'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Enter interactive mode for manual transmission input'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        result = interactive_mode()
    elif args.filepath:
        result = process_transmission_file(args.filepath)
    else:
        parser.print_help()
        return
    
    if result:
        print("🌟 Divine guidance received and processed.")
        print("⚡ May the light illuminate your path.\n")


if __name__ == "__main__":
    main()
