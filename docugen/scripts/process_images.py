#!/usr/bin/env python3
"""
process_images.py - Image optimization and formatting for DocuGen

This script optimizes screenshot images for documentation:
- Compress PNG files to reduce size
- Convert formats if needed
- Resize large images
- Ensure consistent naming

Usage:
    python process_images.py <input_dir> [--output-dir <dir>] [--max-width 1200]

Options:
    --output-dir    Directory for processed images (default: same as input)
    --max-width     Maximum image width in pixels (default: 1200)
    --max-size      Maximum file size in KB (default: 200)
    --format        Output format: png, jpg (default: png)

Dependencies:
    - PIL/Pillow
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


def get_file_size_kb(path: Path) -> float:
    """Get file size in kilobytes."""
    return path.stat().st_size / 1024


def optimize_image(
    input_path: Path,
    output_path: Path,
    max_width: int = 1200,
    max_size_kb: int = 200,
    output_format: str = 'png'
) -> dict:
    """
    Optimize an image for documentation use.

    Args:
        input_path: Path to input image
        output_path: Path to save optimized image
        max_width: Maximum width in pixels
        max_size_kb: Target maximum file size in KB
        output_format: Output format (png or jpg)

    Returns:
        Dict with optimization results
    """
    img = Image.open(input_path)
    original_size = get_file_size_kb(input_path)
    original_dimensions = img.size

    # Resize if too wide
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Convert mode if needed
    if output_format == 'jpg' and img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    elif output_format == 'png' and img.mode == 'P':
        img = img.convert('RGBA')

    # Save with optimization
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == 'png':
        img.save(output_path, 'PNG', optimize=True)
    else:
        # Start with quality 85, reduce if needed
        quality = 85
        img.save(output_path, 'JPEG', quality=quality, optimize=True)

        # Reduce quality if file is still too large
        while get_file_size_kb(output_path) > max_size_kb and quality > 30:
            quality -= 10
            img.save(output_path, 'JPEG', quality=quality, optimize=True)

    final_size = get_file_size_kb(output_path)

    return {
        'input': str(input_path),
        'output': str(output_path),
        'original_size_kb': round(original_size, 2),
        'final_size_kb': round(final_size, 2),
        'original_dimensions': original_dimensions,
        'final_dimensions': img.size,
        'reduction_percent': round((1 - final_size / original_size) * 100, 1) if original_size > 0 else 0
    }


def process_directory(
    input_dir: Path,
    output_dir: Optional[Path],
    max_width: int,
    max_size_kb: int,
    output_format: str
) -> list:
    """
    Process all images in a directory.

    Args:
        input_dir: Directory containing images
        output_dir: Output directory (or None to overwrite)
        max_width: Maximum image width
        max_size_kb: Maximum file size
        output_format: Output format

    Returns:
        List of optimization results
    """
    if output_dir is None:
        output_dir = input_dir

    results = []
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

    for input_path in input_dir.iterdir():
        if input_path.suffix.lower() not in image_extensions:
            continue

        # Determine output path
        output_name = input_path.stem + '.' + output_format
        output_path = output_dir / output_name

        try:
            result = optimize_image(
                input_path,
                output_path,
                max_width,
                max_size_kb,
                output_format
            )
            results.append(result)
            print(f"Processed: {input_path.name} -> {output_path.name} "
                  f"({result['final_size_kb']}KB, {result['reduction_percent']}% reduction)")
        except Exception as e:
            print(f"Error processing {input_path.name}: {e}", file=sys.stderr)
            results.append({
                'input': str(input_path),
                'error': str(e)
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Optimize images for documentation'
    )
    parser.add_argument('input_dir', type=Path, help='Directory containing images')
    parser.add_argument('--output-dir', type=Path, help='Output directory')
    parser.add_argument('--max-width', type=int, default=1200, help='Maximum width (default: 1200)')
    parser.add_argument('--max-size', type=int, default=200, help='Maximum size in KB (default: 200)')
    parser.add_argument('--format', choices=['png', 'jpg'], default='png', help='Output format')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    if not DEPS_AVAILABLE:
        print("Error: PIL/Pillow not installed.", file=sys.stderr)
        print("Run: pip install pillow", file=sys.stderr)
        sys.exit(2)

    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}", file=sys.stderr)
        sys.exit(2)

    if not args.input_dir.is_dir():
        print(f"Error: Not a directory: {args.input_dir}", file=sys.stderr)
        sys.exit(2)

    results = process_directory(
        args.input_dir,
        args.output_dir,
        args.max_width,
        args.max_size,
        args.format
    )

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        # Summary
        successful = [r for r in results if 'error' not in r]
        if successful:
            total_original = sum(r['original_size_kb'] for r in successful)
            total_final = sum(r['final_size_kb'] for r in successful)
            print(f"\nProcessed {len(successful)} images")
            print(f"Total size: {total_original:.1f}KB -> {total_final:.1f}KB")
            if total_original > 0:
                print(f"Overall reduction: {(1 - total_final/total_original) * 100:.1f}%")


if __name__ == '__main__':
    main()
