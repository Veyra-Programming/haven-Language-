"""
Haven Standard Library Methods Registry
Standard: Open Digital Continuity Standard (ODCS) & Standard Library Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Contains over 190+ high-performance, developer-friendly methods spanning
Mathematics, Statistics, Strings, Collections, Chrono, Cryptography, IO, and System.
"""

from typing import Dict, Any, List

# 1. Mathematical & Statistical Methods (50 methods)
from .math_fns import (
    clamp,
    lerp,
    sign,
    abs_val,
    sqrt_val,
    cbrt_val,
    hypot_val,
    pow_mod,
    gcd_val,
    lcm_val,
    factorial_val,
    comb_val,
    perm_val,
    is_prime,
    prime_factors,
    next_prime,
    fibonacci,
    deg_to_rad,
    rad_to_deg,
    sin_val,
    cos_val,
    tan_val,
    asin_val,
    acos_val,
    atan_val,
    atan2_val,
    sinh_val,
    cosh_val,
    tanh_val,
    log_val,
    log2_val,
    log10_val,
    exp_val,
    floor_val,
    ceil_val,
    trunc_val,
    round_to,
    is_close,
    mean_val,
    median_val,
    mode_val,
    variance_val,
    std_dev_val,
    percentile_val,
    z_score,
    covariance_val,
    correlation_val,
    norm_min_max,
    sum_val,
    product_val,
)

# 2. String, Text & NLP Processing Methods (36 methods)
from .string_fns import (
    slugify,
    camel_case,
    snake_case,
    kebab_case,
    pascal_case,
    title_case,
    sponge_case,
    strip_html,
    remove_accents,
    collapse_whitespace,
    truncate_words,
    truncate_chars,
    wrap_text,
    pad_left,
    pad_right,
    center_text,
    word_count,
    char_frequency,
    is_palindrome,
    is_anagram,
    count_vowels,
    count_consonants,
    levenshtein_distance,
    hamming_distance,
    jaccard_similarity,
    to_base64,
    from_base64,
    to_hex_str,
    from_hex_str,
    url_encode_str,
    url_decode_str,
    mask_sensitive,
    rot13,
    reverse_str,
    contains_any,
    contains_all,
)

# 3. Collection, Functional & Iterables Methods (34 methods)
from .collection_fns import (
    chunk_list,
    window_list,
    flatten_list,
    unique_list,
    frequencies_map,
    group_by_key,
    partition_list,
    zip_with_fn,
    intersperse_val,
    compact_list,
    find_first,
    find_last,
    find_index,
    take_while_fn,
    drop_while_fn,
    shuffle_list,
    sample_list,
    cartesian_product,
    permutations_list,
    combinations_list,
    intersect_sets,
    union_sets,
    difference_sets,
    symmetric_difference_sets,
    is_subset_of,
    is_superset_of,
    key_by_fn,
    map_values_dict,
    filter_keys_dict,
    filter_values_dict,
    invert_dict,
    merge_dicts,
    pluck_key,
    sort_by_key,
)

# 4. Chrono, Temporal & Time Continuity Methods (25 methods)
from .chrono_fns import (
    now_utc,
    now_iso,
    now_ms,
    now_micros,
    now_timestamp,
    parse_iso,
    format_iso,
    add_seconds,
    add_minutes,
    add_hours,
    add_days,
    diff_seconds,
    diff_days,
    is_leap_year,
    days_in_month,
    start_of_day,
    end_of_day,
    start_of_month,
    end_of_month,
    start_of_year,
    end_of_year,
    is_weekend,
    humanize_duration,
    sleep_ms,
    monotonic_ms,
)

# 5. Cryptographic, Hashing & Security Methods (20 methods)
from .crypto_fns import (
    sha256_hex,
    sha512_hex,
    sha3_256_hex,
    sha3_512_hex,
    blake2b_hex,
    md5_hex,
    hmac_sha256_hex,
    hmac_sha512_hex,
    pbkdf2_hash_hex,
    constant_time_compare,
    random_bytes_sec,
    random_hex_sec,
    random_token_sec,
    random_int_sec,
    generate_uuid4_str,
    generate_uuid7_str,
    keccak_digest,
    hash_file_sha256,
    mask_hash,
    derive_hkdf,
)

# 6. Filesystem, IO & Path Methods (22 methods)
from .fs_fns import (
    read_text_file,
    write_text_file,
    append_text_file,
    read_bytes_file,
    write_bytes_file,
    read_json_file,
    write_json_file,
    ensure_dir,
    file_exists,
    dir_exists,
    file_size_bytes,
    list_files_in,
    list_dirs_in,
    copy_file_to,
    move_file_to,
    remove_file,
    remove_dir_recursive,
    path_join,
    path_basename,
    path_dirname,
    path_extension,
    canonical_path,
)

# 7. System, Runtime & Diagnostic Methods (12 methods)
from .system_fns import (
    memory_usage_mb,
    cpu_cores_count,
    platform_os_name,
    platform_machine,
    system_hostname,
    get_env_var,
    set_env_var,
    has_env_var,
    process_pid,
    system_uptime_seconds,
    disk_usage_gb,
    force_gc,
)

# Total Methods Count
TOTAL_HAVEN_METHODS = 199


class HavenMethodsCatalog:
    """Provides categorized introspection of all Haven Standard Library Methods."""
    @staticmethod
    def count() -> int:
        return TOTAL_HAVEN_METHODS

    @staticmethod
    def categories() -> Dict[str, int]:
        return {
            "Mathematics & Statistics": 50,
            "Strings, Text & NLP": 36,
            "Collections & Functional": 34,
            "Chrono & Temporal Continuity": 25,
            "Cryptographic & Security": 20,
            "Filesystem, IO & Paths": 22,
            "System & Diagnostics": 12,
        }


methods = HavenMethodsCatalog()
