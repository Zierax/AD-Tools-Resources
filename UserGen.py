#!/usr/bin/env python3
"""
Username Generator for Brute Forcing
Generates username permutations from names.

Usage:
  python3 username_gen.py -i names.txt -o usernames.txt
  python3 username_gen.py -i names.txt -o usernames.txt --format all --years 2020-2024
  python3 username_gen.py -n "John Doe" "Jane Smith" -o usernames.txt
  cat names.txt | python3 username_gen.py -o usernames.txt
"""

import sys
import argparse
import unicodedata
import re
from datetime import datetime

VERSION = "2.0"

def banner():
    """Display tool banner"""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║   Ultimate Username Generator v{VERSION}                    ║
║   Optimized for TryHackMe Machine Brute Forcing          ║
╚═══════════════════════════════════════════════════════════╝
""")

def clean(s):
    """Normalize and clean string"""
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9\s'-]", '', s)
    s = re.sub(r"\s+", ' ', s)
    return s

def generate_variants(first, last, middle='', formats=None):
    """Generate username variants based on formats"""
    f = re.sub(r"[^a-z0-9]", '', first)
    l = re.sub(r"[^a-z0-9]", '', last)
    m = re.sub(r"[^a-z0-9]", '', middle) if middle else ''
    
    if not f:
        return set()
    
    variants = set()
    
    # Choose format types
    if formats is None or 'all' in formats:
        formats = ['standard', 'dotted', 'underscored', 'dashed', 'initial', 'reversed']
    
    # Standard formats (firstname first)
    if 'standard' in formats:
        variants.add(f)  # john
        if l:
            variants.add(f + l)  # johndoe
            variants.add(l + f)  # doejohn (common in AD)
        if m:
            variants.add(f + m)  # johnm
            variants.add(f + m + l)  # johnmdoe
    
    # Dotted formats
    if 'dotted' in formats and l:
        variants.add(f + '.' + l)  # john.doe
        variants.add(l + '.' + f)  # doe.john
        variants.add(f[0] + '.' + l)  # j.doe
        variants.add(f + '.' + l[0])  # john.d
        if m:
            variants.add(f + '.' + m + '.' + l)  # john.m.doe
            variants.add(f[0] + '.' + m[0] + '.' + l)  # j.m.doe
    
    # Underscored formats
    if 'underscored' in formats and l:
        variants.add(f + '_' + l)  # john_doe
        variants.add(l + '_' + f)  # doe_john
        variants.add(f[0] + '_' + l)  # j_doe
        variants.add(f + '_' + l[0])  # john_d
        if m:
            variants.add(f + '_' + m + '_' + l)  # john_m_doe
    
    # Dashed formats
    if 'dashed' in formats and l:
        variants.add(f + '-' + l)  # john-doe
        variants.add(l + '-' + f)  # doe-john
        variants.add(f[0] + '-' + l)  # j-doe
        variants.add(f + '-' + l[0])  # john-d
    
    # Initial-based formats
    if 'initial' in formats and l:
        variants.add(f[0] + l)  # jdoe
        variants.add(l + f[0])  # doej
        variants.add(f + l[0])  # johnd
        variants.add(l[0] + f)  # djohn
        if m:
            variants.add(f[0] + m[0] + l)  # jmdoe
            variants.add(f + m[0] + l[0])  # johnmd
    
    # Reversed formats (lastname first - common in corporate)
    if 'reversed' in formats and l:
        variants.add(l)  # doe
        variants.add(l + f)  # doejohn
        variants.add(l + '.' + f)  # doe.john
        variants.add(l + '_' + f)  # doe_john
        variants.add(l + '-' + f)  # doe-john
    
    return variants

def add_suffixes(usernames, numbers=None, years=None, common_words=None):
    """Add common suffixes to usernames"""
    expanded = set(usernames)
    
    # Add original usernames
    expanded.update(usernames)
    
    # Add numbers
    if numbers:
        for username in usernames:
            for num in numbers:
                expanded.add(username + str(num))
                expanded.add(username + '.' + str(num))
                expanded.add(username + '_' + str(num))
                expanded.add(username + '-' + str(num))
    
    # Add years
    if years:
        for username in usernames:
            for year in years:
                expanded.add(username + str(year))
                expanded.add(username + str(year)[2:])  # Last 2 digits
    
    # Add common words
    if common_words:
        for username in usernames:
            for word in common_words:
                expanded.add(username + word)
                expanded.add(username + '.' + word)
                expanded.add(username + '_' + word)
                expanded.add(username + '-' + word)
    
    return expanded

def add_l33t_speak(usernames):
    """Add l33t speak variations"""
    l33t_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'l': ['1'],
        'g': ['9'],
    }
    
    l33t_variants = set()
    for username in usernames:
        # Apply single character substitution
        for char, replacements in l33t_map.items():
            if char in username:
                for replacement in replacements:
                    l33t_variants.add(username.replace(char, replacement, 1))
    
    return l33t_variants

def add_caps_variations(usernames, caps_type='none'):
    """Add capitalization variations"""
    caps_variants = set()
    
    for username in usernames:
        if caps_type == 'all':
            caps_variants.add(username.upper())  # JOHN
            caps_variants.add(username.capitalize())  # John
            caps_variants.add(username.title())  # John (for dotted names)
        elif caps_type == 'first':
            caps_variants.add(username.capitalize())
        elif caps_type == 'upper':
            caps_variants.add(username.upper())
    
    return caps_variants

def parse_years(year_string):
    """Parse year range or list"""
    years = []
    if not year_string:
        return years
    
    if '-' in year_string:
        start, end = year_string.split('-')
        years = list(range(int(start), int(end) + 1))
    elif ',' in year_string:
        years = [int(y.strip()) for y in year_string.split(',')]
    else:
        years = [int(year_string)]
    
    return years

def parse_numbers(num_string):
    """Parse number range or list"""
    numbers = []
    if not num_string:
        return numbers
    
    if '-' in num_string:
        start, end = num_string.split('-')
        numbers = list(range(int(start), int(end) + 1))
    elif ',' in num_string:
        numbers = [int(n.strip()) for n in num_string.split(',')]
    else:
        numbers = [int(num_string)]
    
    return numbers

def process_name(name, args):
    """Process a single name and generate variants"""
    cleaned = clean(name)
    parts = cleaned.split()
    
    if len(parts) == 0:
        return set()
    
    # Extract first, middle, last
    if len(parts) == 1:
        first = parts[0]
        middle = ''
        last = ''
    elif len(parts) == 2:
        first = parts[0]
        middle = ''
        last = parts[1]
    else:
        first = parts[0]
        middle = parts[1] if len(parts) > 2 else ''
        last = parts[-1]
    
    # Generate base variants
    usernames = generate_variants(first, last, middle, args.format)
    
    # Add suffixes if requested
    if args.numbers or args.years or args.words:
        numbers = parse_numbers(args.numbers) if args.numbers else None
        years = parse_years(args.years) if args.years else None
        words = args.words.split(',') if args.words else None
        usernames = add_suffixes(usernames, numbers, years, words)
    
    # Add l33t speak if requested
    if args.leet:
        usernames.update(add_l33t_speak(usernames))
    
    # Add capitalization variations
    if args.caps != 'none':
        usernames.update(add_caps_variations(usernames, args.caps))
    
    return usernames

def main():
    parser = argparse.ArgumentParser(
        description='',
        epilog='Examples:\n'
               '  %(prog)s -i names.txt -o usernames.txt\n'
               '  %(prog)s -n "John Doe" "Jane Smith" -o users.txt --format all\n'
               '  %(prog)s -i names.txt -o users.txt --numbers 0-99 --years 2020-2024\n'
               '  cat names.txt | %(prog)s -o users.txt --leet --caps first\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('-i', '--input', 
                           help='Input file with names (First Last format, one per line)')
    input_group.add_argument('-n', '--names', nargs='+',
                           help='Names directly from command line')
    
    # Output options
    parser.add_argument('-o', '--output',
                       help='Output file (default: stdout)')
    
    # Format options
    parser.add_argument('-f', '--format', nargs='+',
                       choices=['all', 'standard', 'dotted', 'underscored', 'dashed', 'initial', 'reversed'],
                       default=['all'],
                       help='Username formats to generate (default: all)')
    
    # Suffix options
    parser.add_argument('--numbers', 
                       help='Add number suffixes (e.g., "0-99" or "1,2,3" or "123")')
    parser.add_argument('--years',
                       help='Add year suffixes (e.g., "2020-2024" or "2023,2024")')
    parser.add_argument('--words',
                       help='Add custom word suffixes (comma-separated, e.g., "admin,user,test")')
    
    # Transformation options
    parser.add_argument('--leet', action='store_true',
                       help='Add l33t speak variations (e.g., a->4, e->3, i->1, o->0)')
    parser.add_argument('--caps', choices=['none', 'first', 'upper', 'all'],
                       default='none',
                       help='Add capitalization variations (default: none)')
    
    # Display options
    parser.add_argument('-u', '--unique', action='store_true',
                       help='Output only unique usernames (default behavior)')
    parser.add_argument('-s', '--sort', action='store_true',
                       help='Sort output alphabetically')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress banner and statistics')
    parser.add_argument('-v', '--version', action='version',
                       version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Show banner unless quiet mode
    if not args.quiet:
        banner()
    
    # Collect names from various sources
    names = []
    
    if args.names:
        names = args.names
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[!] Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            names = [line.strip() for line in sys.stdin if line.strip()]
        else:
            parser.print_help()
            sys.exit(1)
    
    if not names:
        print("[!] Error: No names provided", file=sys.stderr)
        sys.exit(1)
    
    # Generate usernames
    if not args.quiet:
        print(f"[*] Processing {len(names)} name(s)...")
    
    all_usernames = set()
    for name in names:
        usernames = process_name(name, args)
        all_usernames.update(usernames)
    
    # Sort if requested
    if args.sort:
        all_usernames = sorted(all_usernames)
    else:
        all_usernames = sorted(all_usernames)  # Still sort for consistency
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                for username in all_usernames:
                    f.write(username + '\n')
            if not args.quiet:
                print(f"[+] Generated {len(all_usernames)} unique usernames")
                print(f"[+] Output saved to: {args.output}")
        except Exception as e:
            print(f"[!] Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Output to stdout
        for username in all_usernames:
            print(username)
        if not args.quiet:
            print(f"\n[+] Generated {len(all_usernames)} unique usernames", file=sys.stderr)

if __name__ == "__main__":
    main()
